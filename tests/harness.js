const fs=require('fs'), vm=require('vm');
const HTML=require('path').join(__dirname,'..','dist','index.html');
function mkEl(id){
  const el={_id:id,id:id,value:'',style:{setProperty(){},removeProperty(){}},dataset:{},_html:'',
    disabled:false,options:[{text:'16:9'}],selectedIndex:0,width:4,height:256,
    clientWidth:1200,clientHeight:800,scrollLeft:0,scrollTop:0,
    classList:{_s:new Set(),add(c){this._s.add(c)},remove(...c){c.forEach(x=>this._s.delete(x))},
      toggle(c,f){f===undefined?(this._s.has(c)?this._s.delete(c):this._s.add(c)):(f?this._s.add(c):this._s.delete(c))},
      contains(c){return this._s.has(c)}},
    _l:{},addEventListener(t,fn){(el._l[t]=el._l[t]||[]).push(fn)},
    appendChild(c){(el._kids=el._kids||[]).push(c);return c},removeChild(){},remove(){},
    setAttribute(k,v){el[k]=v},getAttribute(k){return el[k]},setPointerCapture(){},
    getBoundingClientRect:()=>({left:0,top:0,width:1200,height:800}),
    getContext:()=>({createLinearGradient:()=>({addColorStop(){}}),fillRect(){},drawImage(){},fillStyle:''}),
    toDataURL:()=>'data:image/png;base64,AA',
    querySelectorAll:()=>[],querySelector:()=>mkEl('_c'),closest:()=>null,click(){},
    set innerHTML(v){el._html=v; if(v==='') el._kids=[];},get innerHTML(){return el._html},
    set textContent(v){el._t=v},get textContent(){return el._t||''}};
  return el;
}
function makeHarness(expose,opts){
  opts=opts||{};
  const B=[...fs.readFileSync(HTML,'utf-8').matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
  const store={}, alerts=[];
  const ctx={console,setTimeout:(f)=>{typeof f==='function'&&opts.runTimers&&f()},clearTimeout(){},
    devicePixelRatio:1,requestAnimationFrame:()=>{},innerWidth:1400,innerHeight:900,
    addEventListener:()=>{},removeEventListener:()=>{},
    matchMedia:(q)=>({matches:ctx.__mobile===true,media:q,onchange:null,
      addEventListener(){},removeEventListener(){},addListener(){},removeListener(){},dispatchEvent(){return false;}}),
    localStorage:{_d:(opts&&opts.seed)?{eh_layout_v1:opts.seed}:{},getItem(k){return this._d[k]||null},setItem(k,v){this._d[k]=v},removeItem(k){delete this._d[k]}},
    alert:m=>{alerts.push(m);ctx.__alert=m},confirm:()=>ctx.__confirm!==false,
    prompt:(q,d)=>ctx.__prompt!==undefined?ctx.__prompt:d,
    Image:function(){},Blob:function(a){this.size=a?JSON.stringify(a).length:0},
    URL:{createObjectURL:()=>'blob:x',revokeObjectURL(){}},
    URLSearchParams:global.URLSearchParams,
    location:{origin:'http://localhost',pathname:'/index.html',search:''},
    navigator:{userAgent:'test',clipboard:{writeText(){}}},
    crypto:{getRandomValues:(b)=>{for(let i=0;i<b.length;i++)b[i]=Math.floor(Math.random()*256);return b}},
    fetch:async()=>({ok:true,status:200,json:async()=>({}),text:async()=>''}),
    TextEncoder:global.TextEncoder};
  ctx.window=ctx;ctx.self=ctx;ctx.globalThis=ctx;
  const PANES=['equip','sets','rig','scenes'];
  const getEl=id=>store[id]||(store[id]=mkEl(id));
  const REG={
    '.pane':()=>PANES.map(p=>getEl('pane-'+p)),
    '.rail-btn':()=>PANES.map(p=>{const e=getEl('rail-'+p);e.dataset.p=p;return e;}),
    '#rig-view button':()=>['nest','link','fold'].map(v=>{const e=getEl('rv-'+v);e.dataset.v=v;return e;}),
    '.rail-btn.tool':()=>['scenes','sets','rig'].map(p=>{const e=getEl('railt-'+p);e.dataset.p=p;return e;}),
    '.rail-btn.mode':()=>[getEl('mode-list')],
    '.lockbtn':()=>[getEl('lockbtn-floor'),getEl('lockbtn-3d')],
    '.block':()=>[],'.lrow':()=>[],'.eq-card':()=>[]
  };
  ctx.document={getElementById:getEl,
    querySelectorAll:(sel)=>REG[sel]?REG[sel]():[],querySelector:()=>mkEl('_q'),
    createElement:()=>mkEl('_n'),
    createElementNS:()=>mkEl('_svg'),
    _L:{},
    addEventListener(t,fn){(this._L[t]=this._L[t]||[]).push(fn)},
    removeEventListener(t,fn){const a=this._L[t]||[];const i=a.indexOf(fn);if(i>=0)a.splice(i,1)},
    body:mkEl('body')};
  vm.createContext(ctx);
  if(B.length>1){
    vm.runInContext(B[0],ctx);      // three.js
    ctx.THREE.WebGLRenderer=function(){return{domElement:mkEl('c'),shadowMap:{enabled:false,type:0},
      setPixelRatio(){},setSize(){},getSize(v){v.x=1200;v.y=800;return v},
      setViewport(){},setScissor(){},setScissorTest(){},clearDepth(){},autoClear:true,
      render(){this._n=(this._n||0)+1},outputColorSpace:null,toneMapping:0,toneMappingExposure:1};};
  }
  vm.runInContext(B[B.length-1]+`\n;window.__api={${expose}};`,ctx);
  const fire=(type,ev={})=>{
    const e=Object.assign({key:'',code:'',target:{tagName:'DIV'},preventDefault(){e._pd=true},
      shiftKey:false,altKey:false,ctrlKey:false,metaKey:false},ev);
    (ctx.document._L[type]||[]).forEach(fn=>fn(e));
    return e;
  };
  return {api:ctx.__api,store,ctx,alerts,fire};
}
module.exports={makeHarness,mkEl};
