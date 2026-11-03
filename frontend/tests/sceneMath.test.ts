import {test} from 'node:test';
import assert from 'node:assert/strict';
import {samplePath,replayPose,legPoints,ROUTE_POINTS,worldPoint,type SceneStep} from '../src/sceneMath.ts';

test('path endpoints match restaurant and customer for all three routes',()=>{
  for(const path of Object.values(ROUTE_POINTS)){
    assert.deepEqual(samplePath(path,0).point,[104,258]);
    assert.deepEqual(samplePath(path,1).point,[650,142]);
    assert.deepEqual(samplePath(path,-10).point,[104,258]);
    assert.deepEqual(samplePath(path,5).point,[650,142]);
  }
});
test('sampling follows street segments instead of cutting diagonally through buildings',()=>{
  const path=[[0,0],[10,0],[10,10]]as const;
  assert.deepEqual(samplePath(path,.25).point,[5,0]);
  assert.deepEqual(samplePath(path,.75).point,[10,5]);
  assert.equal(samplePath(path,.25).heading,Math.PI/2);
});
test('continuous playback interpolates only toward a recorded movement',()=>{
  const trace:SceneStep[]=[{step:0,time:5,action:'SELECT_ROUTE',state:'picked_up',route:'A',progress:0},{step:1,time:6,action:'MOVE',state:'in_transit',route:'A',progress:.1}];
  assert.equal(replayPose(trace,0,.5).progress,.05);
  assert.equal(replayPose(trace,0,0).progress,0);
  assert.equal(replayPose(trace,0,1).progress,.1);
  assert.deepEqual(replayPose([],0).point,[104,258]);
});
test('waiting does not move the van and seeking uses the requested saved frame',()=>{
  const trace:SceneStep[]=[{step:0,time:0,action:'ACCEPT_ORDER',state:'accepted',route:null,progress:0},{step:1,time:1,action:'WAIT',state:'preparing',route:null,progress:0},{step:2,time:6,action:'MOVE',state:'in_transit',route:'C',progress:.8}];
  assert.deepEqual(replayPose(trace,0,.9).point,[104,258]);
  assert.deepEqual(replayPose(trace,2,0).point,samplePath(ROUTE_POINTS.C,.8).point);
});
test('reroutes begin at the closure junction without teleporting to restaurant',()=>{
  const trace:SceneStep[]=[{step:0,time:8,action:'ROAD_CLOSED',state:'in_transit',route:'A',progress:.3},{step:1,time:8,action:'REROUTE',state:'in_transit',route:'C',progress:0},{step:2,time:9,action:'MOVE',state:'in_transit',route:'C',progress:.1}];
  assert.deepEqual(replayPose(trace,1).point,replayPose(trace,0).point);
  assert.deepEqual(samplePath(legPoints(trace,2),1).point,[650,142]);
  assert.notDeepEqual(replayPose(trace,1).point,[104,258]);
  const points=legPoints(trace,2);
  for(let i=1;i<points.length;i++)assert.ok(points[i][0]===points[i-1][0]||points[i][1]===points[i-1][1],'Connector must follow orthogonal streets');
});
test('display coordinates do not change simulation coordinates or saved traces',()=>{
  const point=[380,215]as const;assert.deepEqual(worldPoint(point),[0,0,0]);assert.deepEqual(point,[380,215]);
});
