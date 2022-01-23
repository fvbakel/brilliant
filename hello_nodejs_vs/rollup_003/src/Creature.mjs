export class Creature {

    constructor(coordinate) {
        this.coordinate = coordinate;
    }

    move_left(value) {
        this.coordinate.x = this.coordinate.x - value;
    }

    move_right(value) {
        this.coordinate.x = this.coordinate.x + value;
    }

    move_forward(value) {
        this.coordinate.y = this.coordinate.y + value;
    }

    move_backward(value) {
        this.coordinate.y = this.coordinate.y - value;
    }

    move_up(value) {
        this.coordinate.z = this.coordinate.z + value;
    }

    move_down(value) {
        this.coordinate.z = this.coordinate.z - value;
    }

}

