import assert from 'assert';
import { Creature } from '../src/Creature.mjs';

describe('Creature', function() {
  describe('#constructor()', function() {
    it('should be able to create a new creature', function() {
      let creature = new Creature(0,0,0);
      assert.notEqual(creature,null);
      assert.equal([1, 2, 3].indexOf(4), -1);
    });
  });
});