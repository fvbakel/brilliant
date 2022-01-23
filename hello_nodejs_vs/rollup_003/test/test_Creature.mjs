import assert from 'assert';
import { Creature } from '../src/Creature.mjs';
import { Coordinate } from '../src/Coordinate.mjs';

describe('Creature', function() {
  describe('#constructor()', function() {
    it('should be able to create a new creature', function() {
      const coordinate = new Coordinate(0,0,0);
      const creature = new Creature(coordinate);
      assert.notEqual(creature,null);
    });
  });
  describe('#move_forward()', function() {
    it('should be move forward', function() {
      const coordinate = new Coordinate(0,0,0);
      const creature = new Creature(coordinate);
      assert.notEqual(creature,null);
      creature.move_forward(1);
      assert.equal(creature.coordinate.x,0);
      assert.equal(creature.coordinate.y,1);
      assert.equal(creature.coordinate.z,0);
    });
  });
});