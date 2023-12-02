# include <stdio.h>
# include <cjson/cJSON.h>

static const char *response_str = "[{\"time_since_seen_sec\": 213644, \"id\": \"phone-a\"}, {\"time_since_seen_sec\": 269954, \"id\": \"phone-b\"}, {\"time_since_seen_sec\": null, \"id\": \"phone-c\"}, {\"time_since_seen_sec\": 13, \"id\": \"phone-d\"}]";
/*

*/

int main(int argc, char* argv[]) {
    printf("Hello json\n");
    printf("%s",response_str);
    printf("\n");
   
    cJSON *json_device_list = cJSON_Parse(response_str);

    if (json_device_list == NULL) {
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr != NULL)
        {
            fprintf(stderr, "Error before: %s\n", error_ptr);
        }
        return 1;
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
        }
        cJSON *time = cJSON_GetObjectItemCaseSensitive(json_device, "time_since_seen_sec");
        if (cJSON_IsNull(time)) {
            printf("Was never online\n");
        } else if (cJSON_IsNumber(time)) {
            if (time->valueint > 60) {
                printf("More than one minute offline\n");
            } else  {
                printf("Was online in the last 60 sec\n");
            }
        } else {
            printf("Unable to determine if this device was online\n");
        }
    }
    cJSON_Delete(json_device_list);
}