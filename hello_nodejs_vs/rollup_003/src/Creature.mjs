export class Creature {

    constructor(x,y,z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    move_left(value) {
        this.x = this.x - value;
    }

    move_right(value) {
        this.x = this.x + value;
    }

    move_forward(value) {
        this.y = this.y + value;
    }

    move_backward(value) {
        this.y = this.y - value;
    }

    move_up(value) {
        this.y = this.y + value;
    }

    move_down(value) {
        this.y = this.y - value;
    }

}

