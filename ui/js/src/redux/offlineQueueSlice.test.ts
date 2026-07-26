import offlineQueueSlice from './offlineQueueSlice';
import { OfflineOperation } from './types';

const { enqueueOp, dequeueOpByIndex, clearQueue } = offlineQueueSlice.actions;

describe('offlineQueueSlice reducer', function () {
  it('should initialise with empty pendingOps', function () {
    expect(offlineQueueSlice.reducer(undefined, { type: '@@INIT' })).toEqual({
      pendingOps: [],
    });
  });

  describe('enqueueOp', function () {
    it('should append an update op to pendingOps', function () {
      const op: OfflineOperation = {
        type: 'update',
        payload: { id: 1, description: 'updated' },
      };
      const state = offlineQueueSlice.reducer(
        { pendingOps: [] },
        enqueueOp(op),
      );
      expect(state.pendingOps).toEqual([op]);
    });

    it('should append multiple ops in order', function () {
      const op1: OfflineOperation = { type: 'update', payload: { id: 1 } };
      const op2: OfflineOperation = {
        type: 'move',
        payload: { todo_id: 1, relative_id: 2, position: 'after' },
      };
      let state = offlineQueueSlice.reducer({ pendingOps: [] }, enqueueOp(op1));
      state = offlineQueueSlice.reducer(state, enqueueOp(op2));
      expect(state.pendingOps).toEqual([op1, op2]);
    });

    it('should append a create op', function () {
      const op: OfflineOperation = {
        type: 'create',
        payload: { description: 'new todo', labels: ['work'] },
      };
      const state = offlineQueueSlice.reducer(
        { pendingOps: [] },
        enqueueOp(op),
      );
      expect(state.pendingOps).toEqual([op]);
    });
  });

  describe('dequeueOpByIndex', function () {
    it('should remove op at the given index', function () {
      const op1: OfflineOperation = { type: 'update', payload: { id: 1 } };
      const op2: OfflineOperation = { type: 'update', payload: { id: 2 } };
      const state = offlineQueueSlice.reducer(
        { pendingOps: [op1, op2] },
        dequeueOpByIndex(0),
      );
      expect(state.pendingOps).toEqual([op2]);
    });

    it('should remove op at index 1', function () {
      const op1: OfflineOperation = { type: 'update', payload: { id: 1 } };
      const op2: OfflineOperation = { type: 'update', payload: { id: 2 } };
      const state = offlineQueueSlice.reducer(
        { pendingOps: [op1, op2] },
        dequeueOpByIndex(1),
      );
      expect(state.pendingOps).toEqual([op1]);
    });
  });

  describe('clearQueue', function () {
    it('should clear all pending ops', function () {
      const op1: OfflineOperation = { type: 'update', payload: { id: 1 } };
      const op2: OfflineOperation = { type: 'update', payload: { id: 2 } };
      const state = offlineQueueSlice.reducer(
        { pendingOps: [op1, op2] },
        clearQueue(),
      );
      expect(state.pendingOps).toEqual([]);
    });
  });
});

export {};
