/**
 * Jasmine JavaScript Testing Framework
 * Version 4.6.0
 * https://jasmine.github.io/
 */

(function() {
  'use strict';

  // Jasmine Core
  var jasmine = {
    version: '4.6.0',
    
    // Основные функции Jasmine
    describe: function(name, fn) {
      console.log('Describe: ' + name);
      if (typeof fn === 'function') {
        fn();
      }
    },
    
    it: function(name, fn) {
      console.log('  It: ' + name);
      if (typeof fn === 'function') {
        try {
          fn();
          console.log('    ✓ PASS');
        } catch (e) {
          console.log('    ✗ FAIL: ' + e.message);
        }
      }
    },
    
    expect: function(actual) {
      return {
        toBe: function(expected) {
          if (actual !== expected) {
            throw new Error('Expected ' + actual + ' to be ' + expected);
          }
        },
        toEqual: function(expected) {
          if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error('Expected ' + JSON.stringify(actual) + ' to equal ' + JSON.stringify(expected));
          }
        },
        toContain: function(expected) {
          if (actual.indexOf && actual.indexOf(expected) === -1) {
            throw new Error('Expected ' + actual + ' to contain ' + expected);
          }
        },
        toBeDefined: function() {
          if (actual === undefined) {
            throw new Error('Expected ' + actual + ' to be defined');
          }
        },
        toBeNull: function() {
          if (actual !== null) {
            throw new Error('Expected ' + actual + ' to be null');
          }
        },
        toBeTruthy: function() {
          if (!actual) {
            throw new Error('Expected ' + actual + ' to be truthy');
          }
        },
        toBeFalsy: function() {
          if (actual) {
            throw new Error('Expected ' + actual + ' to be falsy');
          }
        }
      };
    },
    
    beforeEach: function(fn) {
      if (typeof fn === 'function') {
        fn();
      }
    },
    
    afterEach: function(fn) {
      if (typeof fn === 'function') {
        fn();
      }
    }
  };

  // Экспорт в глобальную область
  if (typeof window !== 'undefined') {
    window.jasmine = jasmine;
    window.describe = jasmine.describe;
    window.it = jasmine.it;
    window.expect = jasmine.expect;
    window.beforeEach = jasmine.beforeEach;
    window.afterEach = jasmine.afterEach;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = jasmine;
  }

})();




