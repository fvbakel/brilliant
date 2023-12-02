/* HTTP GET Example using plain POSIX sockets

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "protocol_examples_common.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/netdb.h"
#include "lwip/dns.h"
#include "sdkconfig.h"
#include "cJSON.h"
#include "driver/gpio.h"

/* Constants that aren't configurable in menuconfig */
#define WEB_SERVER "192.168.2.206"
#define WEB_PORT "9090"
#define WEB_DEVICES_PATH "/devices/?fields=id,time_since_seen_sec"
#define WEB_REFRESH_PATH "/refresh"

static const char *TAG = "man-monitor";

static const gpio_num_t PINS[] = {GPIO_NUM_27,GPIO_NUM_4,GPIO_NUM_26,GPIO_NUM_25,GPIO_NUM_32};
static const int nr_of_leds = 5;
static const int seconds_active_threshold = 90;
static const int seconds_wait_for_refresh = 60;
static const gpio_num_t alarm_pin = GPIO_NUM_13;
static const gpio_num_t board_pin = GPIO_NUM_22;


static const char *REFRESH_REQUEST = "GET " WEB_REFRESH_PATH " HTTP/1.0\r\n"
    "Host: "WEB_SERVER":"WEB_PORT"\r\n"
    "User-Agent: esp-idf/1.0 esp32\r\n"
    "\r\n";

static const char *DEVICES_REQUEST = "GET " WEB_DEVICES_PATH " HTTP/1.0\r\n"
    "Host: "WEB_SERVER":"WEB_PORT"\r\n"
    "User-Agent: esp-idf/1.0 esp32\r\n"
    "\r\n";

static void configure_leds(void) {
    ESP_LOGI(TAG, "Configure leds");

    for (int i = 0; i < nr_of_leds; i++) {
            
        gpio_reset_pin(PINS[i]);
        /* Set the GPIO as a push/pull output */
        gpio_set_direction(PINS[i], GPIO_MODE_OUTPUT);
    }
    gpio_reset_pin(alarm_pin);
    gpio_set_direction(alarm_pin, GPIO_MODE_OUTPUT);
    gpio_reset_pin(board_pin);
    gpio_set_direction(board_pin, GPIO_MODE_OUTPUT);
}

static int get_index(char *device_name) {
    if (strcmp(device_name,"phone-frank") == 0 ) {
        return 0;
    }
    if (strcmp(device_name,"phone-karin") == 0 ) {
        return 1;
    }
    if (strcmp(device_name,"phone-anke") == 0 ) {
        return 2;
    }
    if (strcmp(device_name,"phone-chris") == 0 ) {
        return 3;
    }
    if (strcmp(device_name,"phone-ilse") == 0 ) {
        return 4;
    }
    return -1;
}

static void raise_alarm() {
    ESP_LOGI(TAG,"Raising alarm!\n");
    for (int i = 0; i < nr_of_leds; i++) {
        gpio_set_level(PINS[i], 0);
    }

    gpio_set_level(alarm_pin, 1);
}

static void reset_alarm() {
    gpio_set_level(alarm_pin, 0);
}

static void set_device_status(char *device_name, uint32_t status) {
    int index = get_index(device_name);
    if (index < 0) {
        raise_alarm();
        return;
    }
    gpio_set_level(PINS[index], status);
}

static void parse_devices_response(char *response_str) {
    ESP_LOGI(TAG,"Parsing:\n%s\n",response_str);
   
    cJSON *json_device_list = cJSON_Parse(response_str);

    if (json_device_list == NULL) {
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr != NULL)
        {
            fprintf(stderr, "Error before: %s\n", error_ptr);
        }
        raise_alarm();
    }
    cJSON *json_device = NULL;
    cJSON_ArrayForEach(json_device,json_device_list) {
        char *string = cJSON_Print(json_device);
        if (string == NULL) {
            printf("string is not defined?\n");

        }
        printf("\nStart parsing:\n%s\n",string);
        cJSON *id = cJSON_GetObjectItemCaseSensitive(json_device, "id");
        if (cJSON_IsString(id) && (id->valuestring != NULL)) {
            printf("Checking device \"%s\"\n", id->valuestring);
        } 
        else {
            printf("Id is not a string?\n");
            raise_alarm();
        }
        cJSON *time = cJSON_GetObjectItemCaseSensitive(json_device, "time_since_seen_sec");
        uint32_t status = 0;
        if (cJSON_IsNull(time)) {
            printf("Was never online\n");
        } else if (cJSON_IsNumber(time)) {
            if (time->valueint > seconds_active_threshold) {
                printf("More than %d seconds offline\n",seconds_active_threshold);
            } else  {
                printf("Was online in the last %d sec\n",seconds_active_threshold);
                status = 1;
            }
        } else {
            printf("Unable to determine if this device was online\n");
            raise_alarm();
        }
        set_device_status(id->valuestring,status);
    }
    cJSON_Delete(json_device_list);
}

static void http_get_task(void *pvParameters)
{
    const struct addrinfo hints = {
        .ai_family = AF_INET,
        .ai_socktype = SOCK_STREAM,
    };
    struct addrinfo *res;
    struct in_addr *addr;
    int s, r;
    char recv_buf[1024];

    while(1) {
        reset_alarm();
        int err = getaddrinfo(WEB_SERVER, WEB_PORT, &hints, &res);

        if(err != 0 || res == NULL) {
            ESP_LOGE(TAG, "DNS lookup failed err=%d res=%p", err, res);
            raise_alarm();
            vTaskDelay(1000 / portTICK_PERIOD_MS);
            continue;
        }

        /* Code to print the resolved IP.

           Note: inet_ntoa is non-reentrant, look at ipaddr_ntoa_r for "real" code */
        addr = &((struct sockaddr_in *)res->ai_addr)->sin_addr;
        ESP_LOGI(TAG, "DNS lookup succeeded. IP=%s", inet_ntoa(*addr));

        s = socket(res->ai_family, res->ai_socktype, 0);
        if(s < 0) {
            ESP_LOGE(TAG, "... Failed to allocate socket.");
            raise_alarm();
            freeaddrinfo(res);
            vTaskDelay(1000 / portTICK_PERIOD_MS);
            continue;
        }
        ESP_LOGI(TAG, "... allocated socket");

        if(connect(s, res->ai_addr, res->ai_addrlen) != 0) {
            ESP_LOGE(TAG, "... socket connect failed errno=%d", errno);
            raise_alarm();
            close(s);
            freeaddrinfo(res);
            vTaskDelay(4000 / portTICK_PERIOD_MS);
            continue;
        }

        ESP_LOGI(TAG, "... connected");
        freeaddrinfo(res);

        /*
            Refresh request
        */
        if (write(s, REFRESH_REQUEST, strlen(REFRESH_REQUEST)) < 0) {
            ESP_LOGE(TAG, "... socket send refresh failed");
            raise_alarm();
            close(s);
            vTaskDelay(4000 / portTICK_PERIOD_MS);
            continue;
        }
        ESP_LOGI(TAG, "... socket send refresh success");

        struct timeval receiving_timeout;
        receiving_timeout.tv_sec = 5;
        receiving_timeout.tv_usec = 0;
        if (setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &receiving_timeout,
                sizeof(receiving_timeout)) < 0) {
            ESP_LOGE(TAG, "... failed to set socket receiving timeout");
            raise_alarm();
            close(s);
            vTaskDelay(4000 / portTICK_PERIOD_MS);
            continue;
        }
        ESP_LOGI(TAG, "... set socket receiving timeout success");

        // Read HTTP response until empty new line
       do {
            bzero(recv_buf, sizeof(recv_buf));
            r = read(s, recv_buf, sizeof(recv_buf)-1);
            char *response_content = strstr(recv_buf, "\r\n\r\n");
            if (response_content != NULL) {
                 ESP_LOGI(TAG, "Response of refresh was: %s",response_content);
            }

        } while(r > 0);
        close(s);
        vTaskDelay(1000 / portTICK_PERIOD_MS);

        /* Devices request*/
        err = getaddrinfo(WEB_SERVER, WEB_PORT, &hints, &res);

        if(err != 0 || res == NULL) {
            ESP_LOGE(TAG, "DNS lookup failed err=%d res=%p", err, res);
            vTaskDelay(1000 / portTICK_PERIOD_MS);
            continue;
        }

        /* Code to print the resolved IP.

           Note: inet_ntoa is non-reentrant, look at ipaddr_ntoa_r for "real" code */
        addr = &((struct sockaddr_in *)res->ai_addr)->sin_addr;
        ESP_LOGI(TAG, "DNS lookup succeeded. IP=%s", inet_ntoa(*addr));

        s = socket(res->ai_family, res->ai_socktype, 0);
        if(s < 0) {
            ESP_LOGE(TAG, "... Failed to allocate socket.");
            raise_alarm();
            freeaddrinfo(res);
            vTaskDelay(1000 / portTICK_PERIOD_MS);
            continue;
        }
        ESP_LOGI(TAG, "... allocated socket");

        if(connect(s, res->ai_addr, res->ai_addrlen) != 0) {
            ESP_LOGE(TAG, "... socket connect failed errno=%d", errno);
            raise_alarm();
            close(s);
            freeaddrinfo(res);
            vTaskDelay(4000 / portTICK_PERIOD_MS);
            continue;
        }

        ESP_LOGI(TAG, "... connected");
        freeaddrinfo(res);

        if (write(s, DEVICES_REQUEST, strlen(DEVICES_REQUEST)) < 0) {
            ESP_LOGE(TAG, "... socket send devices failed");
            raise_alarm();
            close(s);
            vTaskDelay(4000 / portTICK_PERIOD_MS);
            continue;
        }
        ESP_LOGI(TAG, "... socket send devices success");

        //struct timeval receiving_timeout;
        struct timeval receiving_timeout_2;
        receiving_timeout_2.tv_sec = 5;
        receiving_timeout_2.tv_usec = 0;
        if (setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &receiving_timeout_2,
                sizeof(receiving_timeout_2)) < 0) {
            ESP_LOGE(TAG, "... failed to set socket receiving timeout");
            raise_alarm();
            close(s);
            vTaskDelay(4000 / portTICK_PERIOD_MS);
            continue;
        }
        ESP_LOGI(TAG, "... set socket receiving timeout success");

        /* Read HTTP response until empty new line*/
       do {
            bzero(recv_buf, sizeof(recv_buf));
            r = read(s, recv_buf, sizeof(recv_buf)-1);
            ESP_LOGI(TAG, "Reading buffer: %s", recv_buf);
            char *response_content = strstr(recv_buf, "\r\n\r\n");
            if (response_content != NULL && strlen(response_content) > 100) {
                parse_devices_response(response_content);
            }

        } while(r > 0);
 
        ESP_LOGI(TAG, "... done reading from socket. Last read return=%d errno=%d.", r, errno);
        close(s);
        vTaskDelay((seconds_wait_for_refresh * 1000) / portTICK_PERIOD_MS);
        ESP_LOGI(TAG, "Starting again!");
    }
}

void app_main(void)
{
    ESP_ERROR_CHECK( nvs_flash_init() );
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    configure_leds();
    raise_alarm();
    vTaskDelay((1000) / portTICK_PERIOD_MS);
    ESP_ERROR_CHECK(example_connect());

    xTaskCreate(&http_get_task, "http_get_task", 4096, NULL, 5, NULL);
}
