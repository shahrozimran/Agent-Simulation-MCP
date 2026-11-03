/** Display-space geometry. Simulation distances and metrics remain backend-owned. */
export type Vec2 = readonly [number, number];
export type SceneStep = {step:number;time:number;action:string;state:string;route:string|null;progress:number};
export const ROUTE_POINTS:Record<string,readonly Vec2[]> = {
  A:[[104,258],[220,258],[220,198],[510,198],[510,142],[650,142]],
  B:[[104,258],[160,258],[160,350],[560,350],[560,142],[650,142]],
  C:[[104,258],[104,112],[390,112],[390,142],[650,142]],
};
export const ROUTE_COLORS:Record<string,string> = {A:'#d09a48',B:'#729eb1',C:'#23836c'};
export function worldPoint([x,y]:Vec2):[number,number,number] { return [(x-380)/20,0,(y-215)/20]; }
export function samplePath(points:readonly Vec2[],progress:number){
  const lengths=points.slice(1).map((p,i)=>Math.hypot(p[0]-points[i][0],p[1]-points[i][1]));
  let remaining=Math.min(1,Math.max(0,progress))*lengths.reduce((a,b)=>a+b,0);
  for(let i=0;i<lengths.length;i++){
    if(remaining<=lengths[i]||i===lengths.length-1){
      const fraction=lengths[i]?remaining/lengths[i]:0;
      const x=points[i][0]+(points[i+1][0]-points[i][0])*fraction;
      const y=points[i][1]+(points[i+1][1]-points[i][1])*fraction;
      return {point:[x,y] as Vec2,heading:Math.atan2(points[i+1][0]-points[i][0],points[i+1][1]-points[i][1])};
    }
    remaining-=lengths[i];
  }
  return {point:points[0],heading:0};
}
export function legPoints(trace:readonly SceneStep[],index:number):readonly Vec2[]{
  const frame=trace[index];
  if(!frame?.route||!ROUTE_POINTS[frame.route])return ROUTE_POINTS.A;
  for(let i=index;i>=0;i--){
    if(trace[i].action==='REROUTE'&&trace[i].route===frame.route&&i>0){
      // Anchor the new illustrative leg at the recorded emergency junction.
      // No already-traveled cost or distance is changed by rendering.
      const prior=trace[i-1];
      const anchor=samplePath(legPoints(trace,i-1),prior.progress).point;
      // Orthogonal emergency connector avoids a diagonal shortcut through blocks.
      const connector:Vec2[]=[anchor,[220,anchor[1]],[220,frame.route==='C'?112:258]];
      return [...connector,...ROUTE_POINTS[frame.route].slice(frame.route==='C'?2:1)];
    }
  }
  return ROUTE_POINTS[frame.route];
}
export function replayPose(trace:readonly SceneStep[],index:number,phase=0){
  const frame=trace[index];
  if(!frame?.route)return {point:ROUTE_POINTS.A[0],heading:Math.PI/2,progress:0,route:null};
  const next=trace[index+1];
  const canInterpolate=next?.route===frame.route&&next.action==='MOVE'&&next.progress>=frame.progress;
  const progress=canInterpolate?frame.progress+(next.progress-frame.progress)*Math.min(1,Math.max(0,phase)):frame.progress;
  return {...samplePath(legPoints(trace,index),progress),progress,route:frame.route};
}
