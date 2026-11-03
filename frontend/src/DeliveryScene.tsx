import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {Camera,Focus,Layers3,Maximize2,RotateCcw} from 'lucide-react';
import {legPoints,replayPose,samplePath,ROUTE_COLORS,ROUTE_POINTS,worldPoint,type SceneStep,type Vec2} from './sceneMath';

type Scenario={id:string;weather:number;traffic:number[]};
type Props={trace:SceneStep[];step:number;playing:boolean;speed:number;runId?:string;scenario?:Scenario;fallback:React.ReactNode};
type View='orbit'|'top'|'follow';

export default function DeliveryScene(props:Props){
  const host=useRef<HTMLDivElement>(null),latest=useRef(props),controller=useRef<{reset:()=>void}|null>(null);
  const [unavailable,setUnavailable]=useState(false),[view,setView]=useState<View>('orbit'),[inspection,setInspection]=useState<string|null>(null);
  const viewRef=useRef(view),inspectRef=useRef(inspection);
  latest.current=props;viewRef.current=view;inspectRef.current=inspection;
  useEffect(()=>{
    const container=host.current;if(!container)return;
    let renderer:THREE.WebGLRenderer;
    try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});}catch{setUnavailable(true);return;}
    renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.75));
    renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.32;
    renderer.domElement.setAttribute('aria-label','Interactive 3D delivery city. Drag to orbit, scroll to zoom. Camera controls are available below.');
    renderer.domElement.setAttribute('role','img');
    container.appendChild(renderer.domElement);
    const scene=new THREE.Scene();scene.background=new THREE.Color('#e4eae1');scene.fog=new THREE.Fog('#e4eae1',65,115);
    const camera=new THREE.PerspectiveCamera(39,1,0.1,180);
    const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.maxPolarAngle=Math.PI/2.25;controls.minDistance=19;controls.maxDistance=68;controls.target.set(0,0,0);controls.enablePan=true;
    const home=()=>{camera.position.set(29,35,35);controls.target.set(0,0,0);controls.update();};home();
    controller.current={reset:()=>{setView('orbit');home();}};
    scene.add(new THREE.HemisphereLight('#fff6df','#809b82',2.3));
    const sun=new THREE.DirectionalLight('#fff3dc',3.2);sun.position.set(-15,30,15);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-27;sun.shadow.camera.right=27;sun.shadow.camera.top=22;sun.shadow.camera.bottom=-22;sun.shadow.normalBias=.035;sun.shadow.bias=-.0002;scene.add(sun);
    const materials=new Map<string,THREE.MeshStandardMaterial>();
    function material(color:string,roughness=.8){const key=color+roughness;if(!materials.has(key))materials.set(key,new THREE.MeshStandardMaterial({color,roughness}));return materials.get(key)!;}
    function box(w:number,h:number,d:number,color:string,x:number,y:number,z:number,parent:THREE.Object3D=scene){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material(color));m.position.set(x,y,z);m.castShadow=h>.15;m.receiveShadow=true;parent.add(m);return m;}
    function sphere(radius:number,color:string,x:number,y:number,z:number,parent:THREE.Object3D=scene){const m=new THREE.Mesh(new THREE.IcosahedronGeometry(radius,1),material(color));m.position.set(x,y,z);m.castShadow=true;parent.add(m);return m;}
    box(39.5,.7,24.2,'#b8c6b2',0,-.65,0);box(39,.28,23.7,'#e6e4d6',0,-.17,0);
    box(38.4,.12,23.1,'#d5ddc8',0,.01,0);
    // River, banks, and three bridges form a compact low-poly diorama.
    box(2.3,.14,23.2,'#c7d1b7',4.85,.08,0);const river=box(1.85,.1,23.2,'#8ebdc4',4.85,.16,0);
    const ripples:THREE.Mesh[]=[];
    for(let i=0;i<25;i++){const wave=box(.2+(i%4)*.16,.025,.025,'#c0d9d7',4.15+(i%5)*.29,.23,-10.7+i*.86);wave.castShadow=false;ripples.push(wave);}
    // Town streets follow the same display coordinates as the recorded route paths.
    const roadMaterial=material('#65726b');
    const roadSegments=new Set<string>();
    function segment(from:Vec2,to:Vec2,width:number,height:number,mat:THREE.Material,y:number,parent:THREE.Object3D=scene){const a=new THREE.Vector3(...worldPoint(from)),b=new THREE.Vector3(...worldPoint(to));const length=a.distanceTo(b);const mesh=new THREE.Mesh(new THREE.BoxGeometry(width,height,length),mat);mesh.position.copy(a.add(b).multiplyScalar(.5));mesh.position.y=y;mesh.rotation.y=Math.atan2(to[0]-from[0],to[1]-from[1]);mesh.receiveShadow=true;parent.add(mesh);return mesh;}
    function road(points:readonly Vec2[]){for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i];const key=[...a,...b].join(',');if(roadSegments.has(key))continue;roadSegments.add(key);segment(a,b,1.15,.075,material('#c5c9b9'),.13);segment(a,b,.85,.06,roadMaterial,.19);const dist=Math.hypot(b[0]-a[0],b[1]-a[1]);for(let t=12;t<dist-7;t+=17){const start:[number,number]=[a[0]+(b[0]-a[0])*t/dist,a[1]+(b[1]-a[1])*t/dist];const end:[number,number]=[a[0]+(b[0]-a[0])*(t+5)/dist,a[1]+(b[1]-a[1])*(t+5)/dist];segment(start,end,.025,.015,material('#d7d6bc'),.232);}}}
    Object.values(ROUTE_POINTS).forEach(road);
    road([[220,198],[220,112],[390,112]]);
    // Side streets and sidewalks keep the city readable without a map provider.
    road([[65,65],[65,390]]);road([[65,65],[705,65]]);road([[705,65],[705,390]]);road([[65,390],[705,390]]);
    for(const y of [112,142,198,350]){const [, ,z]=worldPoint([477,y]);box(2.6,.2,1.25,'#9fa99a',4.85,.27,z);for(const offset of [-.67,.67])box(2.6,.15,.07,'#c2cbbc',4.85,.46,z+offset);}
    function label(text:string,color:string,x:number,y:number,z:number,width=5){const canvas=document.createElement('canvas');canvas.width=512;canvas.height=96;const ctx=canvas.getContext('2d')!;ctx.fillStyle='rgba(255,254,246,0.95)';ctx.beginPath();ctx.roundRect(6,6,500,84,16);ctx.fill();ctx.font='600 29px Segoe UI';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle=color;ctx.fillText(text,256,49);const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,depthTest:false}));sprite.position.set(x,y,z);sprite.scale.set(width,width*96/512,1);sprite.renderOrder=5;scene.add(sprite);return sprite;}
    let randomState=219;
    const random=()=>{randomState=(randomState*1664525+1013904223)>>>0;return randomState/4294967296;};
    function tree(x:number,z:number,size=1){const group=new THREE.Group();box(.12,.65,.12,'#8f9270',0,.4,0,group);sphere(.52,'#789a65',0,1,0,group);sphere(.36,'#97b17a',.2,1.2,.05,group);group.position.set(x,.13,z);group.scale.setScalar(size);scene.add(group);return group;}
    const trees:THREE.Group[]=[];
    const blocks:[number,number,number,number,number][]=[[45,140,38,47,2],[75,310,44,40,1.4],[175,145,25,32,3.1],[250,145,38,28,3.6],[310,150,40,22,2.2],[350,165,32,20,1.6],[255,225,39,30,1.5],[330,223,40,30,2.5],[250,290,25,45,2.4],[365,290,30,44,1.3],[590,185,42,37,3.8],[650,220,45,41,2.7],[605,285,36,45,2.1],[660,305,35,40,1.6],[590,100,32,25,2.9],[180,300,23,30,1.4],[310,370,38,13,1.2],[420,320,20,30,1.7],[420,85,28,18,1.6],[550,85,22,20,2.8]];
    const palette=['#d1bf9f','#ead9ba','#c1cfba','#d2cabc','#b9c9c7','#ded1b6'];
    blocks.forEach(([px,py,w,d,h],i)=>{const [x,,z]=worldPoint([px,py]);const bw=w/20,bd=d/20;box(bw+.22,.14,bd+.22,'#e6e1cc',x,.22,z);box(bw,h,bd,palette[i%palette.length],x,h/2+.29,z);box(bw+.09,.13,bd+.09,'#e9e1cf',x,h+.32,z);box(bw*.3,.2,bd*.3,'#aeb9aa',x-.15,h+.49,z);for(let floor=.8;floor<h;floor+=.7){for(let col=-bw/2+.23;col<bw/2-.1;col+=.45){box(.19,.28,.025,'#6f8681',x+col,floor+.29,z+bd/2+.015);}}});
    // Two landscaped squares and street trees.
    for(const [px,py,w,d] of [[280,78,100,36],[310,280,70,60]]){const [x,,z]=worldPoint([px,py]);box(w/20,.12,d/20,'#b6c89a',x,.2,z);for(let i=0;i<8;i++)trees.push(tree(x+(random()-.5)*w/23,z+(random()-.5)*d/23,.65+random()*.25));}
    for(const p of [[80,155],[80,180],[79,205],[190,230],[305,90],[350,90],[580,240],[580,320],[680,110],[360,370],[230,365],[120,340]]){const [x,,z]=worldPoint(p as [number,number]);trees.push(tree(x,z,.65));}
    const [rx,,rz]=worldPoint(ROUTE_POINTS.A[0]);
    box(1.8,1.25,1.4,'#e6cdaa',rx,.9,rz+1.25);box(2,.16,1.6,'#657f66',rx,1.6,rz+1.25);box(1.8,.13,.65,'#e8b36e',rx,1.14,rz+.35);for(let i=0;i<5;i++)box(.18,.14,.66,'#fff0d6',rx-.7+i*.35,1.15,rz+.35);box(.38,.73,.04,'#829991',rx,.66,rz+.52);
    const [cx,,cz]=worldPoint(ROUTE_POINTS.A[ROUTE_POINTS.A.length-1]);
    box(1.9,1.5,1.7,'#bdcdb0',cx,1.05,cz-1.5);const roof=new THREE.Mesh(new THREE.ConeGeometry(1.6,.8,4),material('#5c8068'));roof.rotation.y=Math.PI/4;roof.position.set(cx,2.2,cz-1.5);roof.castShadow=true;scene.add(roof);box(.38,.8,.05,'#6f8871',cx,.7,cz-.62);
    label('RESTAURANT','#7e674b',rx,3.05,rz+1.1,4.5);label('CUSTOMER','#35604a',cx,3.6,cz-1.5,4.2);
    label('NORTH PARK','#789064',-5.2,.9,-7.4,3.8);
    // Raised route ribbons and traveling light beads.
    const routes:Record<string,THREE.Group>={},routeMats:Record<string,THREE.MeshStandardMaterial>={};
    const beads:Record<string,THREE.Mesh[]>={};
    function routeRibbon(id:string,points:readonly Vec2[]){const group=new THREE.Group();const mat=new THREE.MeshStandardMaterial({color:ROUTE_COLORS[id],emissive:ROUTE_COLORS[id],emissiveIntensity:.25,transparent:true,opacity:.85,roughness:.55});routeMats[id]=mat;for(let i=1;i<points.length;i++)segment(points[i-1],points[i],.12,.035,mat,.32,group);scene.add(group);routes[id]=group;beads[id]=[];for(let i=0;i<5;i++){const bead=new THREE.Mesh(new THREE.SphereGeometry(.065,8,6),new THREE.MeshBasicMaterial({color:ROUTE_COLORS[id]}));bead.position.y=.39;scene.add(bead);beads[id].push(bead);}}
    for(const [id,points]of Object.entries(ROUTE_POINTS)){routeRibbon(id,points);const mid=points[Math.floor(points.length/2)];const [x,,z]=worldPoint(mid);label(`ROUTE ${id}`,ROUTE_COLORS[id],x,1.45,z,2.3);}
    const ringMat=new THREE.MeshBasicMaterial({color:'#34866b',transparent:true,opacity:.5,side:THREE.DoubleSide});
    const arrivalRing=new THREE.Mesh(new THREE.RingGeometry(.65,.75,48),ringMat);arrivalRing.rotation.x=-Math.PI/2;arrivalRing.position.set(cx,.37,cz);scene.add(arrivalRing);
    function vehicle(color:string,isDelivery=false){const group=new THREE.Group();box(.57,.42,.9,color,0,.46,0,group);box(.5,.36,.5,color,0,.82,-.12,group);box(.44,.21,.025,'#344e4b',0,.84,.14,group);box(.025,.19,.31,'#6c9291',-.26,.82,-.12,group);box(.025,.19,.31,'#6c9291',.26,.82,-.12,group);for(const x of [-.31,.31])for(const z of [-.28,.28]){const wheel=new THREE.Mesh(new THREE.CylinderGeometry(.14,.14,.09,12),material('#37413b'));wheel.rotation.z=Math.PI/2;wheel.position.set(x,.26,z);group.add(wheel);}for(const x of [-.18,.18])box(.1,.07,.025,'#fff1ba',x,.46,.463,group);if(isDelivery){box(.4,.34,.39,'#f1d09a',0,1.12,-.15,group);box(.035,.35,.4,'#cb8f4a',0,1.12,-.15,group);}scene.add(group);return group;}
    const van=vehicle('#256e54',true);van.scale.setScalar(1.15);van.position.set(rx,.22,rz);
    const traffic=Array.from({length:9},(_,i)=>({mesh:vehicle(['#d3a56e','#b8c6bd','#d5cfad','#788c8a'][i%4]),route:['A','B','C'][i%3],offset:random(),rate:.015+random()*.015}));traffic.forEach(car=>car.mesh.scale.setScalar(.68));
    // Rain is one GPU draw call, seeded once; no network assets or physics engine.
    const rainPositions=new Float32Array(420*6);for(let i=0;i<rainPositions.length;i+=6){const x=(random()-.5)*40,y=random()*18,z=(random()-.5)*25;rainPositions.set([x,y,z,x-.04,y-.48,z+.04],i);}
    const rainGeo=new THREE.BufferGeometry();rainGeo.setAttribute('position',new THREE.BufferAttribute(rainPositions,3));const rain=new THREE.LineSegments(rainGeo,new THREE.LineBasicMaterial({color:'#9dbbc4',transparent:true,opacity:.43,depthWrite:false}));scene.add(rain);
    const clouds=new THREE.Group();for(let i=0;i<6;i++){const group=new THREE.Group();for(let j=0;j<3;j++)sphere(.65+j*.12,'#e6e9e4',(j-1)*.8,0,0,group);group.position.set(-17+i*7,9+(i%2),-7+(i%3)*6);group.scale.set(1.6,.5,.9);clouds.add(group);}scene.add(clouds);
    // Road-closure barriers appear exactly when the saved closure event occurs.
    const barrier=new THREE.Group();for(const x of [-.5,.5])box(.08,.5,.08,'#536c5c',x,.42,0,barrier);box(1.3,.25,.09,'#eea86b',0,.65,0,barrier);for(const x of [-.45,-.05,.35])box(.15,.26,.1,'#fff0d3',x,.65,.01,barrier);scene.add(barrier);barrier.visible=false;
    const resize=new ResizeObserver(()=>{const w=container.clientWidth,h=container.clientHeight;if(w&&h){renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}});resize.observe(container);
    let visible=true;const observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;});observer.observe(container);
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');controls.enableDamping=!reduced.matches;
    const raycaster=new THREE.Raycaster();const mouse=new THREE.Vector2();let pointerStart={x:0,y:0};
    const down=(e:PointerEvent)=>{pointerStart={x:e.clientX,y:e.clientY};};
    const up=(e:PointerEvent)=>{if(Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5)return;const rect=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(mouse,camera);const hit=Object.keys(routes).find(id=>raycaster.intersectObject(routes[id],true).length);if(hit)setInspection(hit);};
    renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointerup',up);
    const lost=(e:Event)=>{e.preventDefault();renderer.setAnimationLoop(null);setUnavailable(true);};renderer.domElement.addEventListener('webglcontextlost',lost);
    let last=performance.now(),elapsed=0,phase=0,previousStep=-1,previousRun:string|undefined,previousView:View='orbit',previousScenario='';let closureGeometry='';
    renderer.setAnimationLoop((now:number)=>{
      const delta=Math.min((now-last)/1000,.08);last=now;if(!visible||document.hidden)return;
      const state=latest.current;const frame=state.trace[state.step];const scenario=state.scenario;
      if(previousStep!==state.step||previousRun!==state.runId){phase=0;previousStep=state.step;previousRun=state.runId;}
      if(state.playing&&!reduced.matches)phase=Math.min(1,phase+delta/(.45/state.speed));
      if(!reduced.matches)elapsed+=delta;
      ripples.forEach((wave,i)=>{wave.position.x=4.15+(i%5)*.29+Math.sin(elapsed*.8+i)*.07;});
      trees.forEach((tree,i)=>{tree.rotation.z=Math.sin(elapsed*.7+i)*.012;});
      const pose=replayPose(state.trace,state.step,phase);const [x,,z]=worldPoint(pose.point);van.position.set(x,.22,z);van.rotation.y=pose.heading;
      const rainy=scenario?.weather===1.25;rain.visible=rainy;clouds.visible=rainy;
      if(previousScenario!==scenario?.id){sun.intensity=rainy?1.7:3.2;scene.background=new THREE.Color(rainy?'#dce5e2':'#e4eae1');river.material=material(rainy?'#83abb6':'#8ebdc4');previousScenario=scenario?.id||'';}
      if(rainy&&!reduced.matches){for(let i=0;i<rainPositions.length;i+=6){const drop=delta*12;rainPositions[i+1]-=drop;rainPositions[i+4]-=drop;if(rainPositions[i+1]<.4){rainPositions[i+1]=18;rainPositions[i+4]=17.52;}}rainGeo.attributes.position.needsUpdate=true;clouds.position.x=Math.sin(elapsed*.07)*1.2;}
      const currentLeg=frame?.route?legPoints(state.trace,state.step):null;
      const signature=currentLeg?`${state.runId}:${frame?.route}:${JSON.stringify(currentLeg)}`:'';
      if(signature!==closureGeometry){closureGeometry=signature;for(const[id,group]of Object.entries(routes)){const points=frame?.route===id&&currentLeg?currentLeg:ROUTE_POINTS[id];while(group.children.length){const child=group.children[0] as THREE.Mesh;child.geometry.dispose();group.remove(child);}for(let i=1;i<points.length;i++)segment(points[i-1],points[i],.12,.035,routeMats[id],.32,group);}}
      const focus=inspectRef.current||frame?.route;
      for(const[id,mat]of Object.entries(routeMats)){mat.opacity=focus&&focus!==id ? .22 : .95;mat.emissiveIntensity=focus===id ? .55 : .15;beads[id].forEach((bead,i)=>{const points=frame?.route===id&&currentLeg?currentLeg:ROUTE_POINTS[id];const point=worldPoint(replayPoseForPath(points,(elapsed*.055+i/5)%1));bead.position.set(point[0],.39,point[2]);bead.visible=!focus||focus===id;});}
      traffic.forEach((car,i)=>{const mult=scenario?.traffic[['A','B','C'].indexOf(car.route)]||1;const p=replayPoseForPathWithHeading(ROUTE_POINTS[car.route],(car.offset+elapsed*car.rate/mult)%1);const [tx,,tz]=worldPoint(p.point);car.mesh.position.set(tx+Math.cos(p.heading)*.25,.18,tz-Math.sin(p.heading)*.25);car.mesh.rotation.y=p.heading;car.mesh.visible=i<(scenario?.id==='normal'?5:9);});
      const closure=state.trace.slice(0,state.step+1).find(f=>f.action==='ROAD_CLOSED');barrier.visible=!!closure;if(closure){const p=replayPose(state.trace,state.trace.indexOf(closure));const [bx,,bz]=worldPoint(p.point);barrier.position.set(bx,.25,bz);barrier.rotation.y=p.heading;}
      const delivered=frame?.state==='delivered';arrivalRing.scale.setScalar(delivered?1+Math.sin(elapsed*3)*.13:1);ringMat.opacity=delivered ? .65 : .3;
      if(viewRef.current!==previousView){if(viewRef.current==='top'){camera.position.set(0,49,.01);controls.target.set(0,0,0);}else if(viewRef.current==='orbit')home();previousView=viewRef.current;}
      controls.enabled=viewRef.current!=='follow';
      if(viewRef.current==='follow'){const destination=new THREE.Vector3(x+10,12,z+12);camera.position.lerp(destination,reduced.matches?1:1-Math.exp(-delta*4));controls.target.lerp(new THREE.Vector3(x,0,z),reduced.matches?1:1-Math.exp(-delta*5));camera.lookAt(controls.target);}else controls.update();
      renderer.render(scene,camera);
    });
    return()=>{renderer.setAnimationLoop(null);resize.disconnect();observer.disconnect();controls.dispose();renderer.domElement.removeEventListener('pointerdown',down);renderer.domElement.removeEventListener('pointerup',up);renderer.domElement.removeEventListener('webglcontextlost',lost);const geometries=new Set<THREE.BufferGeometry>();const mats=new Set<THREE.Material>();scene.traverse(object=>{const drawable=object as THREE.Mesh;if(drawable.geometry)geometries.add(drawable.geometry);if(drawable.material){for(const mat of Array.isArray(drawable.material)?drawable.material:[drawable.material])mats.add(mat);}});geometries.forEach(g=>g.dispose());const textures=new Set<THREE.Texture>();mats.forEach(mat=>{const map=(mat as THREE.MeshBasicMaterial).map;if(map)textures.add(map);mat.dispose();});textures.forEach(t=>t.dispose());materials.forEach(m=>m.dispose());renderer.dispose();renderer.domElement.remove();controller.current=null;};
  },[]);
  return <><div className="three-stage" ref={host}/>{unavailable&&<div className="three-fallback">{props.fallback}<span>3D rendering unavailable · showing the route map</span></div>}<div className="scene-badge"><span/>THREE.JS · 3D WORLD</div><div className="scene-toolbar" aria-label="3D camera controls">{([{id:'orbit',label:'Orbit',icon:Layers3},{id:'top',label:'Top view',icon:Maximize2},{id:'follow',label:'Follow van',icon:Focus}]as const).map(item=><button key={item.id} disabled={unavailable} aria-pressed={view===item.id} onClick={()=>setView(item.id)}><item.icon size={13}/>{item.label}</button>)}<button aria-label="Reset 3D camera" disabled={unavailable} onClick={()=>controller.current?.reset()}><RotateCcw size={13}/></button></div><div className="scene-hint"><Camera size={12}/>{view==='follow'?'Camera follows the delivery vehicle':'Drag to orbit · scroll to zoom · right-drag to pan'}</div>{inspection&&<div className="route-inspection"><span style={{background:ROUTE_COLORS[inspection]}}/>Inspecting route {inspection}<button onClick={()=>setInspection(null)}>Clear</button></div>}</>;
}

// Small local wrappers keep geometry sampling independent of Three.js internals.
function replayPoseForPath(points:readonly Vec2[],progress:number){return samplePath(points,progress).point;}
function replayPoseForPathWithHeading(points:readonly Vec2[],progress:number){return samplePath(points,progress);}
