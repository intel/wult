/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),o=new Map;class s{constructor(t,o){if(this._$cssResult$=!0,o!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=o.get(this.cssText);return t&&void 0===e&&(o.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const r=t=>new s("string"==typeof t?t:t+"",e),i=(t,...o)=>{const r=1===t.length?t[0]:o.reduce(((e,o,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(o)+t[s+1]),t[0]);return new s(r,e)},n=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const o of t.cssRules)e+=o.cssText;return r(e)})(t):t;var a;const l=window.trustedTypes,c=l?l.emptyScript:"",d=window.reactiveElementPolyfillSupport,h={toAttribute(t,e){switch(e){case Boolean:t=t?c:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let o=t;switch(e){case Boolean:o=null!==t;break;case Number:o=null===t?null:Number(t);break;case Object:case Array:try{o=JSON.parse(t)}catch(t){o=null}}return o}},u=(t,e)=>e!==t&&(e==e||t==t),p={attribute:!0,type:String,converter:h,reflect:!1,hasChanged:u};class b extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,o)=>{const s=this._$Eh(o,e);void 0!==s&&(this._$Eu.set(s,o),t.push(s))})),t}static createProperty(t,e=p){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const o="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,o,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,o){return{get(){return this[e]},set(s){const r=this[t];this[e]=s,this.requestUpdate(t,r,o)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||p}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const o of e)this.createProperty(o,t[o])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const o=new Set(t.flat(1/0).reverse());for(const t of o)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eh(t,e){const o=e.attribute;return!1===o?void 0:"string"==typeof o?o:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,o;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(o=t.hostConnected)||void 0===o||o.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const o=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,o)=>{t?e.adoptedStyleSheets=o.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):o.forEach((t=>{const o=document.createElement("style"),s=window.litNonce;void 0!==s&&o.setAttribute("nonce",s),o.textContent=t.cssText,e.appendChild(o)}))})(o,this.constructor.elementStyles),o}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,o){this._$AK(t,o)}_$ES(t,e,o=p){var s,r;const i=this.constructor._$Eh(t,o);if(void 0!==i&&!0===o.reflect){const n=(null!==(r=null===(s=o.converter)||void 0===s?void 0:s.toAttribute)&&void 0!==r?r:h.toAttribute)(e,o.type);this._$Ei=t,null==n?this.removeAttribute(i):this.setAttribute(i,n),this._$Ei=null}}_$AK(t,e){var o,s,r;const i=this.constructor,n=i._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=i.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(s=null===(o=a)||void 0===o?void 0:o.fromAttribute)&&void 0!==s?s:"function"==typeof a?a:null)&&void 0!==r?r:h.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,o){let s=!0;void 0!==t&&(((o=o||this.constructor.getPropertyOptions(t)).hasChanged||u)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===o.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,o))):s=!1),!this.isUpdatePending&&s&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const o=this._$AL;try{e=this.shouldUpdate(o),e?(this.willUpdate(o),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(o)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(o)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var v;b.finalized=!0,b.elementProperties=new Map,b.elementStyles=[],b.shadowRootOptions={mode:"open"},null==d||d({ReactiveElement:b}),(null!==(a=globalThis.reactiveElementVersions)&&void 0!==a?a:globalThis.reactiveElementVersions=[]).push("1.3.2");const g=globalThis.trustedTypes,m=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,f=`lit$${(Math.random()+"").slice(9)}$`,y="?"+f,_=`<${y}>`,$=document,w=(t="")=>$.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,x=Array.isArray,C=t=>{var e;return x(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,E=/-->/g,k=/>/g,T=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,U=/'/g,M=/"/g,P=/^(?:script|style|textarea|title)$/i,N=t=>(e,...o)=>({_$litType$:t,strings:e,values:o}),z=N(1),H=(N(2),Symbol.for("lit-noChange")),L=Symbol.for("lit-nothing"),O=new WeakMap,R=(t,e,o)=>{var s,r;const i=null!==(s=null==o?void 0:o.renderBefore)&&void 0!==s?s:e;let n=i._$litPart$;if(void 0===n){const t=null!==(r=null==o?void 0:o.renderBefore)&&void 0!==r?r:null;i._$litPart$=n=new W(e.insertBefore(w(),t),t,void 0,null!=o?o:{})}return n._$AI(t),n},B=$.createTreeWalker($,129,null,!1),D=(t,e)=>{const o=t.length-1,s=[];let r,i=2===e?"<svg>":"",n=S;for(let e=0;e<o;e++){const o=t[e];let a,l,c=-1,d=0;for(;d<o.length&&(n.lastIndex=d,l=n.exec(o),null!==l);)d=n.lastIndex,n===S?"!--"===l[1]?n=E:void 0!==l[1]?n=k:void 0!==l[2]?(P.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=T):void 0!==l[3]&&(n=T):n===T?">"===l[0]?(n=null!=r?r:S,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?T:'"'===l[3]?M:U):n===M||n===U?n=T:n===E||n===k?n=S:(n=T,r=void 0);const h=n===T&&t[e+1].startsWith("/>")?" ":"";i+=n===S?o+_:c>=0?(s.push(a),o.slice(0,c)+"$lit$"+o.slice(c)+f+h):o+f+(-2===c?(s.push(void 0),e):h)}const a=i+(t[o]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==m?m.createHTML(a):a,s]};class I{constructor({strings:t,_$litType$:e},o){let s;this.parts=[];let r=0,i=0;const n=t.length-1,a=this.parts,[l,c]=D(t,e);if(this.el=I.createElement(l,o),B.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=B.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(f)){const o=c[i++];if(t.push(e),void 0!==o){const t=s.getAttribute(o.toLowerCase()+"$lit$").split(f),e=/([.?@])?(.*)/.exec(o);a.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?q:"?"===e[1]?G:"@"===e[1]?Y:V})}else a.push({type:6,index:r})}for(const e of t)s.removeAttribute(e)}if(P.test(s.tagName)){const t=s.textContent.split(f),e=t.length-1;if(e>0){s.textContent=g?g.emptyScript:"";for(let o=0;o<e;o++)s.append(t[o],w()),B.nextNode(),a.push({type:2,index:++r});s.append(t[e],w())}}}else if(8===s.nodeType)if(s.data===y)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=s.data.indexOf(f,t+1));)a.push({type:7,index:r}),t+=f.length-1}r++}}static createElement(t,e){const o=$.createElement("template");return o.innerHTML=t,o}}function F(t,e,o=t,s){var r,i,n,a;if(e===H)return e;let l=void 0!==s?null===(r=o._$Cl)||void 0===r?void 0:r[s]:o._$Cu;const c=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==c&&(null===(i=null==l?void 0:l._$AO)||void 0===i||i.call(l,!1),void 0===c?l=void 0:(l=new c(t),l._$AT(t,o,s)),void 0!==s?(null!==(n=(a=o)._$Cl)&&void 0!==n?n:a._$Cl=[])[s]=l:o._$Cu=l),void 0!==l&&(e=F(t,l._$AS(t,e.values),l,s)),e}class j{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:o},parts:s}=this._$AD,r=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:$).importNode(o,!0);B.currentNode=r;let i=B.nextNode(),n=0,a=0,l=s[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new W(i,i.nextSibling,this,t):1===l.type?e=new l.ctor(i,l.name,l.strings,this,t):6===l.type&&(e=new Z(i,this,t)),this.v.push(e),l=s[++a]}n!==(null==l?void 0:l.index)&&(i=B.nextNode(),n++)}return r}m(t){let e=0;for(const o of this.v)void 0!==o&&(void 0!==o.strings?(o._$AI(t,o,e),e+=o.strings.length-2):o._$AI(t[e])),e++}}class W{constructor(t,e,o,s){var r;this.type=2,this._$AH=L,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=o,this.options=s,this._$Cg=null===(r=null==s?void 0:s.isConnected)||void 0===r||r}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=F(this,t,e),A(t)?t===L||null==t||""===t?(this._$AH!==L&&this._$AR(),this._$AH=L):t!==this._$AH&&t!==H&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):C(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==L&&A(this._$AH)?this._$AA.nextSibling.data=t:this.k($.createTextNode(t)),this._$AH=t}T(t){var e;const{values:o,_$litType$:s}=t,r="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=I.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===r)this._$AH.m(o);else{const t=new j(r,this),e=t.p(this.options);t.m(o),this.k(e),this._$AH=t}}_$AC(t){let e=O.get(t.strings);return void 0===e&&O.set(t.strings,e=new I(t)),e}S(t){x(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let o,s=0;for(const r of t)s===e.length?e.push(o=new W(this.M(w()),this.M(w()),this,this.options)):o=e[s],o._$AI(r),s++;s<e.length&&(this._$AR(o&&o._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var o;for(null===(o=this._$AP)||void 0===o||o.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class V{constructor(t,e,o,s,r){this.type=1,this._$AH=L,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=r,o.length>2||""!==o[0]||""!==o[1]?(this._$AH=Array(o.length-1).fill(new String),this.strings=o):this._$AH=L}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,o,s){const r=this.strings;let i=!1;if(void 0===r)t=F(this,t,e,0),i=!A(t)||t!==this._$AH&&t!==H,i&&(this._$AH=t);else{const s=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=F(this,s[o+n],e,n),a===H&&(a=this._$AH[n]),i||(i=!A(a)||a!==this._$AH[n]),a===L?t=L:t!==L&&(t+=(null!=a?a:"")+r[n+1]),this._$AH[n]=a}i&&!s&&this.C(t)}C(t){t===L?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class q extends V{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===L?void 0:t}}const K=g?g.emptyScript:"";class G extends V{constructor(){super(...arguments),this.type=4}C(t){t&&t!==L?this.element.setAttribute(this.name,K):this.element.removeAttribute(this.name)}}class Y extends V{constructor(t,e,o,s,r){super(t,e,o,s,r),this.type=5}_$AI(t,e=this){var o;if((t=null!==(o=F(this,t,e,0))&&void 0!==o?o:L)===H)return;const s=this._$AH,r=t===L&&s!==L||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==L&&(s===L||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,o;"function"==typeof this._$AH?this._$AH.call(null!==(o=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==o?o:this.element,t):this._$AH.handleEvent(t)}}class Z{constructor(t,e,o){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=o}get _$AU(){return this._$AM._$AU}_$AI(t){F(this,t)}}const J={L:"$lit$",P:f,V:y,I:1,N:D,R:j,j:C,D:F,H:W,F:V,O:G,W:Y,B:q,Z},X=window.litHtmlPolyfillSupport;var Q,tt;null==X||X(I,W),(null!==(v=globalThis.litHtmlVersions)&&void 0!==v?v:globalThis.litHtmlVersions=[]).push("2.2.5");class et extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const o=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=o.firstChild),o}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=R(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return H}}et.finalized=!0,et._$litElement$=!0,null===(Q=globalThis.litElementHydrateSupport)||void 0===Q||Q.call(globalThis,{LitElement:et});const ot=globalThis.litElementPolyfillSupport;null==ot||ot({LitElement:et}),(null!==(tt=globalThis.litElementVersions)&&void 0!==tt?tt:globalThis.litElementVersions=[]).push("3.2.0"),Object.create;var st=Object.defineProperty,rt=Object.defineProperties,it=Object.getOwnPropertyDescriptor,nt=Object.getOwnPropertyDescriptors,at=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),lt=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),ct=Object.prototype.propertyIsEnumerable,dt=(t,e,o)=>e in t?st(t,e,{enumerable:!0,configurable:!0,writable:!0,value:o}):t[e]=o,ht=(t,e)=>{for(var o in e||(e={}))lt.call(e,o)&&dt(t,o,e[o]);if(at)for(var o of at(e))ct.call(e,o)&&dt(t,o,e[o]);return t},ut=(t,e)=>rt(t,nt(e)),pt=(t,e,o,s)=>{for(var r,i=s>1?void 0:s?it(e,o):e,n=t.length-1;n>=0;n--)(r=t[n])&&(i=(s?r(e,o,i):r(i))||i);return s&&i&&st(e,o,i),i};function bt(t,e,o){return new Promise((s=>{if((null==o?void 0:o.duration)===1/0)throw new Error("Promise-based animations must be finite.");const r=t.animate(e,ut(ht({},o),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:o.duration}));r.addEventListener("cancel",s,{once:!0}),r.addEventListener("finish",s,{once:!0})}))}function vt(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const o=requestAnimationFrame(e);t.addEventListener("cancel",(()=>o),{once:!0}),t.addEventListener("finish",(()=>o),{once:!0}),t.cancel()})))))}function gt(t,e){return t.map((t=>ut(ht({},t),{height:"auto"===t.height?`${e}px`:t.height})))}var mt=new Map,ft=new WeakMap;function yt(t,e){mt.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function _t(t,e){const o=ft.get(t);if(null==o?void 0:o[e])return o[e];return mt.get(e)||{keyframes:[],options:{duration:0}}}var $t,wt,At=class{constructor(t,...e){this.slotNames=[],(this.host=t).addController(this),this.slotNames=e,this.handleSlotChange=this.handleSlotChange.bind(this)}hasDefaultSlot(){return[...this.host.childNodes].some((t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1}))}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}handleSlotChange(t){const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()}},xt=t=>(...e)=>({_$litDirective$:t,values:e}),Ct=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,o){this._$Ct=t,this._$AM=e,this._$Ci=o}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},St=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Et=Symbol(),kt=new Map,Tt=class{constructor(t,e){if(this._$cssResult$=!0,e!==Et)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=kt.get(this.cssText);return St&&void 0===t&&(kt.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},Ut=t=>new Tt("string"==typeof t?t:t+"",Et),Mt=(t,...e)=>{const o=1===t.length?t[0]:e.reduce(((e,o,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(o)+t[s+1]),t[0]);return new Tt(o,Et)},Pt=St?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const o of t.cssRules)e+=o.cssText;return Ut(e)})(t):t,Nt=window.trustedTypes,zt=Nt?Nt.emptyScript:"",Ht=window.reactiveElementPolyfillSupport,Lt={toAttribute(t,e){switch(e){case Boolean:t=t?zt:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let o=t;switch(e){case Boolean:o=null!==t;break;case Number:o=null===t?null:Number(t);break;case Object:case Array:try{o=JSON.parse(t)}catch(t){o=null}}return o}},Ot=(t,e)=>e!==t&&(e==e||t==t),Rt={attribute:!0,type:String,converter:Lt,reflect:!1,hasChanged:Ot},Bt=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,o)=>{const s=this._$Eh(o,e);void 0!==s&&(this._$Eu.set(s,o),t.push(s))})),t}static createProperty(t,e=Rt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const o="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,o,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,o){return{get(){return this[e]},set(s){const r=this[t];this[e]=s,this.requestUpdate(t,r,o)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Rt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const o of e)this.createProperty(o,t[o])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const o=new Set(t.flat(1/0).reverse());for(const t of o)e.unshift(Pt(t))}else void 0!==t&&e.push(Pt(t));return e}static _$Eh(t,e){const o=e.attribute;return!1===o?void 0:"string"==typeof o?o:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,o;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(o=t.hostConnected)||void 0===o||o.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return o=e,s=this.constructor.elementStyles,St?o.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const e=document.createElement("style"),s=window.litNonce;void 0!==s&&e.setAttribute("nonce",s),e.textContent=t.cssText,o.appendChild(e)})),e;var o,s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,o){this._$AK(t,o)}_$ES(t,e,o=Rt){var s,r;const i=this.constructor._$Eh(t,o);if(void 0!==i&&!0===o.reflect){const n=(null!==(r=null===(s=o.converter)||void 0===s?void 0:s.toAttribute)&&void 0!==r?r:Lt.toAttribute)(e,o.type);this._$Ei=t,null==n?this.removeAttribute(i):this.setAttribute(i,n),this._$Ei=null}}_$AK(t,e){var o,s,r;const i=this.constructor,n=i._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=i.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(s=null===(o=a)||void 0===o?void 0:o.fromAttribute)&&void 0!==s?s:"function"==typeof a?a:null)&&void 0!==r?r:Lt.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,o){let s=!0;void 0!==t&&(((o=o||this.constructor.getPropertyOptions(t)).hasChanged||Ot)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===o.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,o))):s=!1),!this.isUpdatePending&&s&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const o=this._$AL;try{e=this.shouldUpdate(o),e?(this.willUpdate(o),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(o)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(o)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}};Bt.finalized=!0,Bt.elementProperties=new Map,Bt.elementStyles=[],Bt.shadowRootOptions={mode:"open"},null==Ht||Ht({ReactiveElement:Bt}),(null!==($t=globalThis.reactiveElementVersions)&&void 0!==$t?$t:globalThis.reactiveElementVersions=[]).push("1.3.2");var Dt=globalThis.trustedTypes,It=Dt?Dt.createPolicy("lit-html",{createHTML:t=>t}):void 0,Ft=`lit$${(Math.random()+"").slice(9)}$`,jt="?"+Ft,Wt=`<${jt}>`,Vt=document,qt=(t="")=>Vt.createComment(t),Kt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Gt=Array.isArray,Yt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Zt=/-->/g,Jt=/>/g,Xt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,Qt=/'/g,te=/"/g,ee=/^(?:script|style|textarea|title)$/i,oe=t=>(e,...o)=>({_$litType$:t,strings:e,values:o}),se=oe(1),re=oe(2),ie=Symbol.for("lit-noChange"),ne=Symbol.for("lit-nothing"),ae=new WeakMap,le=Vt.createTreeWalker(Vt,129,null,!1),ce=class{constructor({strings:t,_$litType$:e},o){let s;this.parts=[];let r=0,i=0;const n=t.length-1,a=this.parts,[l,c]=((t,e)=>{const o=t.length-1,s=[];let r,i=2===e?"<svg>":"",n=Yt;for(let e=0;e<o;e++){const o=t[e];let a,l,c=-1,d=0;for(;d<o.length&&(n.lastIndex=d,l=n.exec(o),null!==l);)d=n.lastIndex,n===Yt?"!--"===l[1]?n=Zt:void 0!==l[1]?n=Jt:void 0!==l[2]?(ee.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=Xt):void 0!==l[3]&&(n=Xt):n===Xt?">"===l[0]?(n=null!=r?r:Yt,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Xt:'"'===l[3]?te:Qt):n===te||n===Qt?n=Xt:n===Zt||n===Jt?n=Yt:(n=Xt,r=void 0);const h=n===Xt&&t[e+1].startsWith("/>")?" ":"";i+=n===Yt?o+Wt:c>=0?(s.push(a),o.slice(0,c)+"$lit$"+o.slice(c)+Ft+h):o+Ft+(-2===c?(s.push(void 0),e):h)}const a=i+(t[o]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==It?It.createHTML(a):a,s]})(t,e);if(this.el=ce.createElement(l,o),le.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=le.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(Ft)){const o=c[i++];if(t.push(e),void 0!==o){const t=s.getAttribute(o.toLowerCase()+"$lit$").split(Ft),e=/([.?@])?(.*)/.exec(o);a.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?ve:"?"===e[1]?me:"@"===e[1]?fe:be})}else a.push({type:6,index:r})}for(const e of t)s.removeAttribute(e)}if(ee.test(s.tagName)){const t=s.textContent.split(Ft),e=t.length-1;if(e>0){s.textContent=Dt?Dt.emptyScript:"";for(let o=0;o<e;o++)s.append(t[o],qt()),le.nextNode(),a.push({type:2,index:++r});s.append(t[e],qt())}}}else if(8===s.nodeType)if(s.data===jt)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=s.data.indexOf(Ft,t+1));)a.push({type:7,index:r}),t+=Ft.length-1}r++}}static createElement(t,e){const o=Vt.createElement("template");return o.innerHTML=t,o}};function de(t,e,o=t,s){var r,i,n,a;if(e===ie)return e;let l=void 0!==s?null===(r=o._$Cl)||void 0===r?void 0:r[s]:o._$Cu;const c=Kt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==c&&(null===(i=null==l?void 0:l._$AO)||void 0===i||i.call(l,!1),void 0===c?l=void 0:(l=new c(t),l._$AT(t,o,s)),void 0!==s?(null!==(n=(a=o)._$Cl)&&void 0!==n?n:a._$Cl=[])[s]=l:o._$Cu=l),void 0!==l&&(e=de(t,l._$AS(t,e.values),l,s)),e}var he,ue,pe=class{constructor(t,e,o,s){var r;this.type=2,this._$AH=ne,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=o,this.options=s,this._$Cg=null===(r=null==s?void 0:s.isConnected)||void 0===r||r}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=de(this,t,e),Kt(t)?t===ne||null==t||""===t?(this._$AH!==ne&&this._$AR(),this._$AH=ne):t!==this._$AH&&t!==ie&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):(t=>{var e;return Gt(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==ne&&Kt(this._$AH)?this._$AA.nextSibling.data=t:this.k(Vt.createTextNode(t)),this._$AH=t}T(t){var e;const{values:o,_$litType$:s}=t,r="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=ce.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===r)this._$AH.m(o);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:o},parts:s}=this._$AD,r=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Vt).importNode(o,!0);le.currentNode=r;let i=le.nextNode(),n=0,a=0,l=s[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new pe(i,i.nextSibling,this,t):1===l.type?e=new l.ctor(i,l.name,l.strings,this,t):6===l.type&&(e=new ye(i,this,t)),this.v.push(e),l=s[++a]}n!==(null==l?void 0:l.index)&&(i=le.nextNode(),n++)}return r}m(t){let e=0;for(const o of this.v)void 0!==o&&(void 0!==o.strings?(o._$AI(t,o,e),e+=o.strings.length-2):o._$AI(t[e])),e++}}(r,this),e=t.p(this.options);t.m(o),this.k(e),this._$AH=t}}_$AC(t){let e=ae.get(t.strings);return void 0===e&&ae.set(t.strings,e=new ce(t)),e}S(t){Gt(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let o,s=0;for(const r of t)s===e.length?e.push(o=new pe(this.M(qt()),this.M(qt()),this,this.options)):o=e[s],o._$AI(r),s++;s<e.length&&(this._$AR(o&&o._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var o;for(null===(o=this._$AP)||void 0===o||o.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},be=class{constructor(t,e,o,s,r){this.type=1,this._$AH=ne,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=r,o.length>2||""!==o[0]||""!==o[1]?(this._$AH=Array(o.length-1).fill(new String),this.strings=o):this._$AH=ne}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,o,s){const r=this.strings;let i=!1;if(void 0===r)t=de(this,t,e,0),i=!Kt(t)||t!==this._$AH&&t!==ie,i&&(this._$AH=t);else{const s=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=de(this,s[o+n],e,n),a===ie&&(a=this._$AH[n]),i||(i=!Kt(a)||a!==this._$AH[n]),a===ne?t=ne:t!==ne&&(t+=(null!=a?a:"")+r[n+1]),this._$AH[n]=a}i&&!s&&this.C(t)}C(t){t===ne?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},ve=class extends be{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===ne?void 0:t}},ge=Dt?Dt.emptyScript:"",me=class extends be{constructor(){super(...arguments),this.type=4}C(t){t&&t!==ne?this.element.setAttribute(this.name,ge):this.element.removeAttribute(this.name)}},fe=class extends be{constructor(t,e,o,s,r){super(t,e,o,s,r),this.type=5}_$AI(t,e=this){var o;if((t=null!==(o=de(this,t,e,0))&&void 0!==o?o:ne)===ie)return;const s=this._$AH,r=t===ne&&s!==ne||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==ne&&(s===ne||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,o;"function"==typeof this._$AH?this._$AH.call(null!==(o=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==o?o:this.element,t):this._$AH.handleEvent(t)}},ye=class{constructor(t,e,o){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=o}get _$AU(){return this._$AM._$AU}_$AI(t){de(this,t)}},_e=window.litHtmlPolyfillSupport;null==_e||_e(ce,pe),(null!==(wt=globalThis.litHtmlVersions)&&void 0!==wt?wt:globalThis.litHtmlVersions=[]).push("2.2.4");var $e=class extends Bt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const o=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=o.firstChild),o}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,o)=>{var s,r;const i=null!==(s=null==o?void 0:o.renderBefore)&&void 0!==s?s:e;let n=i._$litPart$;if(void 0===n){const t=null!==(r=null==o?void 0:o.renderBefore)&&void 0!==r?r:null;i._$litPart$=n=new pe(e.insertBefore(qt(),t),t,void 0,null!=o?o:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return ie}};$e.finalized=!0,$e._$litElement$=!0,null===(he=globalThis.litElementHydrateSupport)||void 0===he||he.call(globalThis,{LitElement:$e});var we=globalThis.litElementPolyfillSupport;null==we||we({LitElement:$e}),(null!==(ue=globalThis.litElementVersions)&&void 0!==ue?ue:globalThis.litElementVersions=[]).push("3.2.0");var Ae=xt(class extends Ct{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var o,s;if(void 0===this.et){this.et=new Set,void 0!==t.strings&&(this.st=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(o=this.st)||void 0===o?void 0:o.has(t))&&this.et.add(t);return this.render(e)}const r=t.element.classList;this.et.forEach((t=>{t in e||(r.remove(t),this.et.delete(t))}));for(const t in e){const o=!!e[t];o===this.et.has(t)||(null===(s=this.st)||void 0===s?void 0:s.has(t))||(o?(r.add(t),this.et.add(t)):(r.remove(t),this.et.delete(t)))}return ie}}),xe=Mt`
  :host {
    box-sizing: border-box;
  }

  :host *,
  :host *::before,
  :host *::after {
    box-sizing: inherit;
  }

  [hidden] {
    display: none !important;
  }
`,Ce=Mt`
  ${xe}

  :host {
    display: contents;

    /* For better DX, we'll reset the margin here so the base part can inherit it */
    margin: 0;
  }

  .alert {
    position: relative;
    display: flex;
    align-items: stretch;
    background-color: var(--sl-panel-background-color);
    border: solid var(--sl-panel-border-width) var(--sl-panel-border-color);
    border-top-width: calc(var(--sl-panel-border-width) * 3);
    border-radius: var(--sl-border-radius-medium);
    box-shadow: var(--box-shadow);
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-small);
    font-weight: var(--sl-font-weight-normal);
    line-height: 1.6;
    color: var(--sl-color-neutral-700);
    margin: inherit;
  }

  .alert:not(.alert--has-icon) .alert__icon,
  .alert:not(.alert--closable) .alert__close-button {
    display: none;
  }

  .alert__icon {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-large);
    padding-left: var(--sl-spacing-large);
  }

  .alert--primary {
    border-top-color: var(--sl-color-primary-600);
  }

  .alert--primary .alert__icon {
    color: var(--sl-color-primary-600);
  }

  .alert--success {
    border-top-color: var(--sl-color-success-600);
  }

  .alert--success .alert__icon {
    color: var(--sl-color-success-600);
  }

  .alert--neutral {
    border-top-color: var(--sl-color-neutral-600);
  }

  .alert--neutral .alert__icon {
    color: var(--sl-color-neutral-600);
  }

  .alert--warning {
    border-top-color: var(--sl-color-warning-600);
  }

  .alert--warning .alert__icon {
    color: var(--sl-color-warning-600);
  }

  .alert--danger {
    border-top-color: var(--sl-color-danger-600);
  }

  .alert--danger .alert__icon {
    color: var(--sl-color-danger-600);
  }

  .alert__message {
    flex: 1 1 auto;
    padding: var(--sl-spacing-large);
    overflow: hidden;
  }

  .alert__close-button {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-large);
    padding-right: var(--sl-spacing-medium);
  }
`;function Se(t,e){const o=ht({waitUntilFirstUpdate:!1},e);return(e,s)=>{const{update:r}=e;if(t in e){const i=t;e.update=function(t){if(t.has(i)){const e=t.get(i),r=this[i];e!==r&&(o.waitUntilFirstUpdate&&!this.hasUpdated||this[s](e,r))}r.call(this,t)}}}}function Ee(t,e,o){const s=new CustomEvent(e,ht({bubbles:!0,cancelable:!1,composed:!0,detail:{}},o));return t.dispatchEvent(s),s}function ke(t,e){return new Promise((o=>{t.addEventListener(e,(function s(r){r.target===t&&(t.removeEventListener(e,s),o())}))}))}var Te=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:o,elements:s}=e;return{kind:o,elements:s,finisher(e){window.customElements.define(t,e)}}})(t,e),Ue=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?ut(ht({},e),{finisher(o){o.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(o){o.createProperty(e.key,t)}};function Me(t){return(e,o)=>void 0!==o?((t,e,o)=>{e.constructor.createProperty(o,t)})(t,e,o):Ue(t,e)}function Pe(t){return Me(ut(ht({},t),{state:!0}))}var Ne;function ze(t,e){return(({finisher:t,descriptor:e})=>(o,s)=>{var r;if(void 0===s){const s=null!==(r=o.originalKey)&&void 0!==r?r:o.key,i=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(o.key)}:ut(ht({},o),{key:s});return null!=t&&(i.finisher=function(e){t(e,s)}),i}{const r=o.constructor;void 0!==e&&Object.defineProperty(o,s,e(s)),null==t||t(r,s)}})({descriptor:o=>{const s={get(){var e,o;return null!==(o=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==o?o:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof o?Symbol():"__"+o;s.get=function(){var o,s;return void 0===this[e]&&(this[e]=null!==(s=null===(o=this.renderRoot)||void 0===o?void 0:o.querySelector(t))&&void 0!==s?s:null),this[e]}}return s}})}null===(Ne=window.HTMLSlotElement)||void 0===Ne||Ne.prototype.assignedElements;var He=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Le=class extends $e{constructor(){super(...arguments),this.hasSlotController=new At(this,"icon","suffix"),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,ke(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,ke(this,"sl-after-hide")}async toast(){return new Promise((t=>{null===He.parentElement&&document.body.append(He),He.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{He.removeChild(this),t(),null===He.querySelector("sl-alert")&&He.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){Ee(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await vt(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=_t(this,"alert.show");await bt(this.base,t,e),Ee(this,"sl-after-show")}else{Ee(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await vt(this.base);const{keyframes:t,options:e}=_t(this,"alert.hide");await bt(this.base,t,e),this.base.hidden=!0,Ee(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return se`
      <div
        part="base"
        class=${Ae({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--has-icon":this.hasSlotController.test("icon"),"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        aria-hidden=${this.open?"false":"true"}
        @mousemove=${this.handleMouseMove}
      >
        <span part="icon" class="alert__icon">
          <slot name="icon"></slot>
        </span>

        <span part="message" class="alert__message">
          <slot></slot>
        </span>

        ${this.closable?se`
              <sl-icon-button
                part="close-button"
                exportparts="base:close-button__base"
                class="alert__close-button"
                name="x"
                library="system"
                @click=${this.handleCloseClick}
              ></sl-icon-button>
            `:""}
      </div>
    `}};Le.styles=Ce,pt([ze('[part="base"]')],Le.prototype,"base",2),pt([Me({type:Boolean,reflect:!0})],Le.prototype,"open",2),pt([Me({type:Boolean,reflect:!0})],Le.prototype,"closable",2),pt([Me({reflect:!0})],Le.prototype,"variant",2),pt([Me({type:Number})],Le.prototype,"duration",2),pt([Se("open",{waitUntilFirstUpdate:!0})],Le.prototype,"handleOpenChange",1),pt([Se("duration")],Le.prototype,"handleDurationChange",1),Le=pt([Te("sl-alert")],Le),yt("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),yt("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var Oe=(()=>{const t=document.createElement("style");let e;try{document.head.appendChild(t),t.sheet.insertRule(":focus-visible { color: inherit }"),e=!0}catch(t){e=!1}finally{t.remove()}return e})(),Re=Ut(Oe?":focus-visible":":focus"),Be=Mt`
  ${xe}

  :host {
    display: inline-block;
  }

  .icon-button {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    background: none;
    border: none;
    border-radius: var(--sl-border-radius-medium);
    font-size: inherit;
    color: var(--sl-color-neutral-600);
    padding: var(--sl-spacing-x-small);
    cursor: pointer;
    transition: var(--sl-transition-medium) color;
    -webkit-appearance: none;
  }

  .icon-button:hover:not(.icon-button--disabled),
  .icon-button:focus:not(.icon-button--disabled) {
    color: var(--sl-color-primary-600);
  }

  .icon-button:active:not(.icon-button--disabled) {
    color: var(--sl-color-primary-700);
  }

  .icon-button:focus {
    outline: none;
  }

  .icon-button--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .icon-button${Re} {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }
`,De=Symbol.for(""),Ie=t=>{var e,o;if((null===(e=t)||void 0===e?void 0:e.r)===De)return null===(o=t)||void 0===o?void 0:o._$litStatic$},Fe=(t,...e)=>({_$litStatic$:e.reduce(((e,o,s)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(o)+t[s+1]),t[0]),r:De}),je=new Map,We=t=>(e,...o)=>{const s=o.length;let r,i;const n=[],a=[];let l,c=0,d=!1;for(;c<s;){for(l=e[c];c<s&&void 0!==(i=o[c],r=Ie(i));)l+=r+e[++c],d=!0;a.push(i),n.push(l),c++}if(c===s&&n.push(e[s]),d){const t=n.join("$$lit$$");void 0===(e=je.get(t))&&(n.raw=n,je.set(t,e=n)),o=a}return t(e,...o)},Ve=We(se),qe=(We(re),t=>null!=t?t:ne),Ke=class extends $e{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Ee(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Ee(this,"sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}render(){const t=!!this.href,e=t?Fe`a`:Fe`button`;return Ve`
      <${e}
        part="base"
        class=${Ae({"icon-button":!0,"icon-button--disabled":!t&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${qe(t?void 0:this.disabled)}
        type=${qe(t?void 0:"button")}
        href=${qe(t?this.href:void 0)}
        target=${qe(t?this.target:void 0)}
        download=${qe(t?this.download:void 0)}
        rel=${qe(t&&this.target?"noreferrer noopener":void 0)}
        role=${qe(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          name=${qe(this.name)}
          library=${qe(this.library)}
          src=${qe(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${e}>
    `}};Ke.styles=Be,pt([Pe()],Ke.prototype,"hasFocus",2),pt([ze(".icon-button")],Ke.prototype,"button",2),pt([Me()],Ke.prototype,"name",2),pt([Me()],Ke.prototype,"library",2),pt([Me()],Ke.prototype,"src",2),pt([Me()],Ke.prototype,"href",2),pt([Me()],Ke.prototype,"target",2),pt([Me()],Ke.prototype,"download",2),pt([Me()],Ke.prototype,"label",2),pt([Me({type:Boolean,reflect:!0})],Ke.prototype,"disabled",2),Ke=pt([Te("sl-icon-button")],Ke);var Ge="";function Ye(t){Ge=t}var Ze=[...document.getElementsByTagName("script")],Je=Ze.find((t=>t.hasAttribute("data-shoelace")));if(Je)Ye(Je.getAttribute("data-shoelace"));else{const t=Ze.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let e="";t&&(e=t.getAttribute("src")),Ye(e.split("/").slice(0,-1).join("/"))}var Xe={"check-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">\n      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"></path>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},Qe=[{name:"default",resolver:t=>`${Ge.replace(/\/$/,"")}/assets/icons/${t}.svg`},{name:"system",resolver:t=>t in Xe?`data:image/svg+xml,${encodeURIComponent(Xe[t])}`:""}],to=[];function eo(t){return Qe.find((e=>e.name===t))}var oo=new Map,so=new Map;var ro=Mt`
  ${xe}

  :host {
    display: inline-block;
    width: 1em;
    height: 1em;
    contain: strict;
    box-sizing: content-box !important;
  }

  .icon,
  svg {
    display: block;
    height: 100%;
    width: 100%;
  }
`,io=class extends Ct{constructor(t){if(super(t),this.it=ne,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===ne||null==t)return this.ft=void 0,this.it=t;if(t===ie)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.ft;this.it=t;const e=[t];return e.raw=e,this.ft={_$litType$:this.constructor.resultType,strings:e,values:[]}}};io.directiveName="unsafeHTML",io.resultType=1,xt(io);var no=class extends io{};no.directiveName="unsafeSVG",no.resultType=2;var ao=xt(no),lo=new DOMParser,co=class extends $e{constructor(){super(...arguments),this.svg="",this.label="",this.library="default"}connectedCallback(){super.connectedCallback(),to.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,to=to.filter((e=>e!==t))}getUrl(){const t=eo(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){var t;const e=eo(this.library),o=this.getUrl();if(o)try{const s=await async function(t){if(so.has(t))return so.get(t);const e=await function(t,e="cors"){if(oo.has(t))return oo.get(t);const o=fetch(t,{mode:e}).then((async t=>({ok:t.ok,status:t.status,html:await t.text()})));return oo.set(t,o),o}(t),o={ok:e.ok,status:e.status,svg:null};if(e.ok){const t=document.createElement("div");t.innerHTML=e.html;const s=t.firstElementChild;o.svg="svg"===(null==s?void 0:s.tagName.toLowerCase())?s.outerHTML:""}return so.set(t,o),o}(o);if(o!==this.getUrl())return;if(s.ok){const o=lo.parseFromString(s.svg,"text/html").body.querySelector("svg");null!==o?(null==(t=null==e?void 0:e.mutator)||t.call(e,o),this.svg=o.outerHTML,Ee(this,"sl-load")):(this.svg="",Ee(this,"sl-error"))}else this.svg="",Ee(this,"sl-error")}catch(t){Ee(this,"sl-error")}else this.svg.length>0&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return se` <div
      part="base"
      class="icon"
      role=${qe(t?"img":void 0)}
      aria-label=${qe(t?this.label:void 0)}
      aria-hidden=${qe(t?void 0:"true")}
    >
      ${ao(this.svg)}
    </div>`}};co.styles=ro,pt([Pe()],co.prototype,"svg",2),pt([Me({reflect:!0})],co.prototype,"name",2),pt([Me()],co.prototype,"src",2),pt([Me()],co.prototype,"label",2),pt([Me({reflect:!0})],co.prototype,"library",2),pt([Se("name"),Se("src"),Se("library")],co.prototype,"setIcon",1),co=pt([Te("sl-icon")],co);const ho=t=>(...e)=>({_$litDirective$:t,values:e});class uo{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,o){this._$Ct=t,this._$AM=e,this._$Ci=o}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const{H:po}=J,bo=(t,e)=>{var o,s;return void 0===e?void 0!==(null===(o=t)||void 0===o?void 0:o._$litType$):(null===(s=t)||void 0===s?void 0:s._$litType$)===e},vo=()=>document.createComment(""),go=(t,e,o)=>{var s;const r=t._$AA.parentNode,i=void 0===e?t._$AB:e._$AA;if(void 0===o){const e=r.insertBefore(vo(),i),s=r.insertBefore(vo(),i);o=new po(e,s,t,t.options)}else{const e=o._$AB.nextSibling,n=o._$AM,a=n!==t;if(a){let e;null===(s=o._$AQ)||void 0===s||s.call(o,t),o._$AM=t,void 0!==o._$AP&&(e=t._$AU)!==n._$AU&&o._$AP(e)}if(e!==i||a){let t=o._$AA;for(;t!==e;){const e=t.nextSibling;r.insertBefore(t,i),t=e}}}return o},mo={},fo=(t,e=mo)=>t._$AH=e,yo=t=>t._$AH,_o=(t,e)=>{var o,s;const r=t._$AN;if(void 0===r)return!1;for(const t of r)null===(s=(o=t)._$AO)||void 0===s||s.call(o,e,!1),_o(t,e);return!0},$o=t=>{let e,o;do{if(void 0===(e=t._$AM))break;o=e._$AN,o.delete(t),t=e}while(0===(null==o?void 0:o.size))},wo=t=>{for(let e;e=t._$AM;t=e){let o=e._$AN;if(void 0===o)e._$AN=o=new Set;else if(o.has(t))break;o.add(t),Co(e)}};function Ao(t){void 0!==this._$AN?($o(this),this._$AM=t,wo(this)):this._$AM=t}function xo(t,e=!1,o=0){const s=this._$AH,r=this._$AN;if(void 0!==r&&0!==r.size)if(e)if(Array.isArray(s))for(let t=o;t<s.length;t++)_o(s[t],!1),$o(s[t]);else null!=s&&(_o(s,!1),$o(s));else _o(this,t)}const Co=t=>{var e,o,s,r;2==t.type&&(null!==(e=(s=t)._$AP)&&void 0!==e||(s._$AP=xo),null!==(o=(r=t)._$AQ)&&void 0!==o||(r._$AQ=Ao))};class So extends uo{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,o){super._$AT(t,e,o),wo(this),this.isConnected=t._$AU}_$AO(t,e=!0){var o,s;t!==this.isConnected&&(this.isConnected=t,t?null===(o=this.reconnected)||void 0===o||o.call(this):null===(s=this.disconnected)||void 0===s||s.call(this)),e&&(_o(this,t),$o(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Eo{constructor(t){this.U=t}disconnect(){this.U=void 0}reconnect(t){this.U=t}deref(){return this.U}}class ko{constructor(){this.Y=void 0,this.q=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Y=this.q=void 0}}const To=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,Uo=ho(class extends So{constructor(){super(...arguments),this._$Cwt=1073741823,this._$Cyt=[],this._$CG=new Eo(this),this._$CK=new ko}render(...t){var e;return null!==(e=t.find((t=>!To(t))))&&void 0!==e?e:H}update(t,e){const o=this._$Cyt;let s=o.length;this._$Cyt=e;const r=this._$CG,i=this._$CK;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cwt);t++){const n=e[t];if(!To(n))return this._$Cwt=t,n;t<s&&n===o[t]||(this._$Cwt=1073741823,s=0,Promise.resolve(n).then((async t=>{for(;i.get();)await i.get();const e=r.deref();if(void 0!==e){const o=e._$Cyt.indexOf(n);o>-1&&o<e._$Cwt&&(e._$Cwt=o,e.setValue(t))}})))}return H}disconnected(){this._$CG.disconnect(),this._$CK.pause()}reconnected(){this._$CG.reconnect(this),this._$CK.resume()}});class Mo{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class Po extends et{static properties={src:{type:String},template:{attribute:!1}};static styles=i`
        table {
            table-layout: fixed;
            border-collapse: collapse;
            width: auto;
        }

        table th {
            font-family: Arial, sans-serif;
            font-size: 15px;
            font-weight: bold;
            padding: 10px 5px;
            border-style: solid;
            border-width: 1px;
            overflow: hidden;
            word-break: normal;
            border-color: black;
            text-align: center;
            background-color: rgb(161, 195, 209);
        }

        table td {
            font-family: Arial, sans-serif;
            font-size: 14px;
            padding: 5px 10px;
            border-style: solid;
            border-width: 1px;
            overflow: hidden;
            word-break:normal ;
            border-color:black;
            background-color: rgb(237, 250, 255);
        }

        table .td-colname {
            font-size: 15px;
            font-weight: bold;
            text-align: left;
        }

        table .td-value {
            text-align: left;
        }

        table .td-funcname {
            text-align: left;
        }
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),o=(await fetch(t)).body.getReader();let{value:s,done:r}=await o.read();s=s?e.decode(s,{stream:!0}):"";const i=/\r\n|\n|\r/gm;let n=0;for(;;){const t=i.exec(s);if(t)yield s.substring(n,t.index),n=i.lastIndex;else{if(r)break;const t=s.substr(n);({value:s,done:r}=await o.read()),s=t+(s?e.decode(s,{stream:!0}):""),n=i.lastIndex=0}}n<s.length&&(yield s.substr(n))}render(){if(!this.src)return z``;const t=this.parseSrc();return z`${Uo(t,z``)}`}}customElements.define("report-table",Po),customElements.define("intro-tbl",class extends Po{parseHeader(t){const e=t.split(";");return z`
            <tr>
                ${e.map((t=>z`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=z``,o=!0;for(const s of t.split(";")){const[t,r,i]=s.split("|");let n=z`${t}`;i&&(n=z`<a href=${i}>${n}</a>`),r&&(n=z`<abbr title=${r}>${n}</abbr>`),o?(e=z`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,o=!1):e=z`${e}
                    <td>
                        ${n}
                    </td>
                `}return z`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.src);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Mo("first line in intro table file should be a header.");e=e.slice(2);let o=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Mo("lines following the first should all be normal table rows.");e=e.slice(2),o=z`${o}${this.parseRow(e)}`}return z`<table>${o}</table>`}});var No=Mt`
  ${xe}

  :host {
    --track-color: var(--sl-color-neutral-200);
    --indicator-color: var(--sl-color-primary-600);

    display: block;
  }

  .tab-group {
    display: flex;
    border: solid 1px transparent;
    border-radius: 0;
  }

  .tab-group .tab-group__tabs {
    display: flex;
    position: relative;
  }

  .tab-group .tab-group__indicator {
    position: absolute;
    left: 0;
    transition: var(--sl-transition-fast) transform ease, var(--sl-transition-fast) width ease;
  }

  .tab-group--has-scroll-controls .tab-group__nav-container {
    position: relative;
    padding: 0 var(--sl-spacing-x-large);
  }

  .tab-group__scroll-button {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    bottom: 0;
    width: var(--sl-spacing-x-large);
  }

  .tab-group__scroll-button--start {
    left: 0;
  }

  .tab-group__scroll-button--end {
    right: 0;
  }

  /*
   * Top
   */

  .tab-group--top {
    flex-direction: column;
  }

  .tab-group--top .tab-group__nav-container {
    order: 1;
  }

  .tab-group--top .tab-group__nav {
    display: flex;
    overflow-x: auto;

    /* Hide scrollbar in Firefox */
    scrollbar-width: none;
  }

  /* Hide scrollbar in Chrome/Safari */
  .tab-group--top .tab-group__nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .tab-group--top .tab-group__tabs {
    flex: 1 1 auto;
    position: relative;
    flex-direction: row;
    border-bottom: solid 2px var(--track-color);
  }

  .tab-group--top .tab-group__indicator {
    bottom: -2px;
    border-bottom: solid 2px var(--indicator-color);
  }

  .tab-group--top .tab-group__body {
    order: 2;
  }

  .tab-group--top ::slotted(sl-tab-panel) {
    --padding: var(--sl-spacing-medium) 0;
  }

  /*
   * Bottom
   */

  .tab-group--bottom {
    flex-direction: column;
  }

  .tab-group--bottom .tab-group__nav-container {
    order: 2;
  }

  .tab-group--bottom .tab-group__nav {
    display: flex;
    overflow-x: auto;

    /* Hide scrollbar in Firefox */
    scrollbar-width: none;
  }

  /* Hide scrollbar in Chrome/Safari */
  .tab-group--bottom .tab-group__nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .tab-group--bottom .tab-group__tabs {
    flex: 1 1 auto;
    position: relative;
    flex-direction: row;
    border-top: solid 2px var(--track-color);
  }

  .tab-group--bottom .tab-group__indicator {
    top: calc(-1 * 2px);
    border-top: solid 2px var(--indicator-color);
  }

  .tab-group--bottom .tab-group__body {
    order: 1;
  }

  .tab-group--bottom ::slotted(sl-tab-panel) {
    --padding: var(--sl-spacing-medium) 0;
  }

  /*
   * Start
   */

  .tab-group--start {
    flex-direction: row;
  }

  .tab-group--start .tab-group__nav-container {
    order: 1;
  }

  .tab-group--start .tab-group__tabs {
    flex: 0 0 auto;
    flex-direction: column;
    border-right: solid 2px var(--track-color);
  }

  .tab-group--start .tab-group__indicator {
    right: calc(-1 * 2px);
    border-right: solid 2px var(--indicator-color);
  }

  .tab-group--start .tab-group__body {
    flex: 1 1 auto;
    order: 2;
  }

  .tab-group--start ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }

  /*
   * End
   */

  .tab-group--end {
    flex-direction: row;
  }

  .tab-group--end .tab-group__nav-container {
    order: 2;
  }

  .tab-group--end .tab-group__tabs {
    flex: 0 0 auto;
    flex-direction: column;
    border-left: solid 2px var(--track-color);
  }

  .tab-group--end .tab-group__indicator {
    left: calc(-1 * 2px);
    border-left: solid 2px var(--indicator-color);
  }

  .tab-group--end .tab-group__body {
    flex: 1 1 auto;
    order: 1;
  }

  .tab-group--end ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }
`;function zo(t,e,o="vertical",s="smooth"){const r=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),i=r.top+e.scrollTop,n=r.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,c=e.scrollTop,d=e.scrollTop+e.offsetHeight;"horizontal"!==o&&"both"!==o||(n<a?e.scrollTo({left:n,behavior:s}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:s})),"vertical"!==o&&"both"!==o||(i<c?e.scrollTo({top:i,behavior:s}):i+t.clientHeight>d&&e.scrollTo({top:i-e.offsetHeight+t.clientHeight,behavior:s}))}var Ho,Lo=new Set,Oo=new MutationObserver(Do),Ro=new Map,Bo=document.documentElement.lang||navigator.language;function Do(){Bo=document.documentElement.lang||navigator.language,[...Lo.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}Oo.observe(document.documentElement,{attributes:!0,attributeFilter:["lang"]});var Io=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Lo.add(this.host)}hostDisconnected(){Lo.delete(this.host)}term(t,...e){return function(t,e,...o){const s=t.toLowerCase().slice(0,2),r=t.length>2?t.toLowerCase():"",i=Ro.get(r),n=Ro.get(s);let a;if(i&&i[e])a=i[e];else if(n&&n[e])a=n[e];else{if(!Ho||!Ho[e])return console.error(`No translation found for: ${e}`),e;a=Ho[e]}return"function"==typeof a?a(...o):a}(this.host.lang||Bo,t,...e)}date(t,e){return function(t,e,o){return e=new Date(e),new Intl.DateTimeFormat(t,o).format(e)}(this.host.lang||Bo,t,e)}number(t,e){return function(t,e,o){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(t,o).format(e)}(this.host.lang||Bo,t,e)}relativeTime(t,e,o){return function(t,e,o,s){return new Intl.RelativeTimeFormat(t,s).format(e,o)}(this.host.lang||Bo,t,e,o)}};!function(...t){t.map((t=>{const e=t.$code.toLowerCase();Ro.set(e,t),Ho||(Ho=t)})),Do()}({$code:"en",$name:"English",$dir:"ltr",clearEntry:"Clear entry",close:"Close",copy:"Copy",currentValue:"Current value",hidePassword:"Hide password",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",toggleColorFormat:"Toggle color format"});var Fo=class extends $e{constructor(){super(...arguments),this.localize=new Io(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{var o;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(o=this.getActiveTab())?o:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t=!1){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement;if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){let o=this.tabs.indexOf(e);"Home"===t.key?o=0:"End"===t.key?o=this.tabs.length-1:["top","bottom"].includes(this.placement)&&"ArrowLeft"===t.key||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?o--:(["top","bottom"].includes(this.placement)&&"ArrowRight"===t.key||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&o++,o<0&&(o=this.tabs.length-1),o>this.tabs.length-1&&(o=0),this.tabs[o].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[o],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&zo(this.tabs[o],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth}setActiveTab(t,e){if(e=ht({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const o=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)})),this.syncIndicator(),["top","bottom"].includes(this.placement)&&zo(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(o&&Ee(this,"sl-tab-hide",{detail:{name:o.panel}}),Ee(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,o=t.clientHeight,s=this.getAllTabs(!0),r=s.slice(0,s.indexOf(t)).reduce(((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight})),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=`translateX(${r.left}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${o}px`,this.indicator.style.transform=`translateY(${r.top}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.panels=this.getAllPanels(),this.syncIndicator()}render(){return se`
      <div
        part="base"
        class=${Ae({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?se`
                <sl-icon-button
                  part="scroll-button scroll-button--start"
                  exportparts="base:scroll-button__base"
                  class="tab-group__scroll-button tab-group__scroll-button--start"
                  name="chevron-left"
                  library="system"
                  label=${this.localize.term("scrollToStart")}
                  @click=${this.handleScrollToStart}
                ></sl-icon-button>
              `:""}

          <div class="tab-group__nav">
            <div part="tabs" class="tab-group__tabs" role="tablist">
              <div part="active-tab-indicator" class="tab-group__indicator"></div>
              <slot name="nav" @slotchange=${this.syncTabsAndPanels}></slot>
            </div>
          </div>

          ${this.hasScrollControls?se`
                <sl-icon-button
                  part="scroll-button scroll-button--end"
                  exportparts="base:scroll-button__base"
                  class="tab-group__scroll-button tab-group__scroll-button--end"
                  name="chevron-right"
                  library="system"
                  label=${this.localize.term("scrollToEnd")}
                  @click=${this.handleScrollToEnd}
                ></sl-icon-button>
              `:""}
        </div>

        <div part="body" class="tab-group__body">
          <slot @slotchange=${this.syncTabsAndPanels}></slot>
        </div>
      </div>
    `}};Fo.styles=No,pt([ze(".tab-group")],Fo.prototype,"tabGroup",2),pt([ze(".tab-group__body")],Fo.prototype,"body",2),pt([ze(".tab-group__nav")],Fo.prototype,"nav",2),pt([ze(".tab-group__indicator")],Fo.prototype,"indicator",2),pt([Pe()],Fo.prototype,"hasScrollControls",2),pt([Me()],Fo.prototype,"placement",2),pt([Me()],Fo.prototype,"activation",2),pt([Me({attribute:"no-scroll-controls",type:Boolean})],Fo.prototype,"noScrollControls",2),pt([Me()],Fo.prototype,"lang",2),pt([Se("noScrollControls",{waitUntilFirstUpdate:!0})],Fo.prototype,"updateScrollControls",1),pt([Se("placement",{waitUntilFirstUpdate:!0})],Fo.prototype,"syncIndicator",1),Fo=pt([Te("sl-tab-group")],Fo);var jo=0;function Wo(){return++jo}var Vo=Mt`
  ${xe}

  :host {
    display: inline-block;
  }

  .tab {
    display: inline-flex;
    align-items: center;
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-small);
    font-weight: var(--sl-font-weight-semibold);
    border-radius: var(--sl-border-radius-medium);
    color: var(--sl-color-neutral-600);
    padding: var(--sl-spacing-medium) var(--sl-spacing-large);
    white-space: nowrap;
    user-select: none;
    cursor: pointer;
    transition: var(--transition-speed) box-shadow, var(--transition-speed) color;
  }

  .tab:hover:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab:focus {
    outline: none;
  }

  .tab${Re}:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
    outline: var(--sl-focus-ring);
    outline-offset: calc(-1 * var(--sl-focus-ring-width) - var(--sl-focus-ring-offset));
  }

  .tab.tab--active:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab.tab--closable {
    padding-right: var(--sl-spacing-small);
  }

  .tab.tab--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tab__close-button {
    font-size: var(--sl-font-size-large);
    margin-left: var(--sl-spacing-2x-small);
  }

  .tab__close-button::part(base) {
    padding: var(--sl-spacing-3x-small);
  }
`,qo=class extends $e{constructor(){super(...arguments),this.localize=new Io(this),this.attrId=Wo(),this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Ee(this,"sl-close")}render(){return this.id=this.id.length>0?this.id:this.componentId,se`
      <div
        part="base"
        class=${Ae({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        role="tab"
        aria-disabled=${this.disabled?"true":"false"}
        aria-selected=${this.active?"true":"false"}
        tabindex=${this.disabled||!this.active?"-1":"0"}
      >
        <slot></slot>
        ${this.closable?se`
              <sl-icon-button
                part="close-button"
                exportparts="base:close-button__base"
                name="x"
                library="system"
                label=${this.localize.term("close")}
                class="tab__close-button"
                @click=${this.handleCloseClick}
                tabindex="-1"
              ></sl-icon-button>
            `:""}
      </div>
    `}};qo.styles=Vo,pt([ze(".tab")],qo.prototype,"tab",2),pt([Me({reflect:!0})],qo.prototype,"panel",2),pt([Me({type:Boolean,reflect:!0})],qo.prototype,"active",2),pt([Me({type:Boolean})],qo.prototype,"closable",2),pt([Me({type:Boolean,reflect:!0})],qo.prototype,"disabled",2),pt([Me()],qo.prototype,"lang",2),qo=pt([Te("sl-tab")],qo);var Ko=Mt`
  ${xe}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }
`,Go=class extends $e{constructor(){super(...arguments),this.attrId=Wo(),this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId}render(){return this.style.display=this.active?"block":"none",se`
      <div part="base" class="tab-panel" role="tabpanel" aria-hidden=${this.active?"false":"true"}>
        <slot></slot>
      </div>
    `}};Go.styles=Ko,pt([Me({reflect:!0})],Go.prototype,"name",2),pt([Me({type:Boolean,reflect:!0})],Go.prototype,"active",2),Go=pt([Te("sl-tab-panel")],Go);const Yo=ho(class extends uo{constructor(t){super(t),this.tt=new WeakMap}render(t){return[t]}update(t,[e]){if(bo(this.it)&&(!bo(e)||this.it.strings!==e.strings)){const e=yo(t).pop();let o=this.tt.get(this.it.strings);if(void 0===o){const t=document.createDocumentFragment();o=R(L,t),o.setConnected(!1),this.tt.set(this.it.strings,o)}fo(o,[e]),go(o,void 0,e)}if(bo(e)){if(!bo(this.it)||this.it.strings!==e.strings){const o=this.tt.get(e.strings);if(void 0!==o){const e=yo(o).pop();(t=>{t._$AR()})(t),go(t,void 0,e),fo(t,[e])}}this.it=e}else this.it=void 0;return this.render(e)}});class Zo extends et{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(t,e){for(const e of t)"active"===e.attributeName&&(this.tabname===e.target.id?this.visible=!0:this.visible=!1)}connectedCallback(){super.connectedCallback();const t=this.checkVisible.bind(this);this.observer=new MutationObserver(t),this.observer.observe(this.parentElement,{attributes:!0})}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return z`
        ${Yo(this.visible?z`${this.visibleTemplate()}`:z``)}`}}customElements.define("wult-tab",Zo);var Jo=Mt`
  ${xe}

  :host {
    --track-width: 2px;
    --track-color: rgb(128 128 128 / 25%);
    --indicator-color: var(--sl-color-primary-600);
    --speed: 2s;

    display: inline-flex;
    width: 1em;
    height: 1em;
  }

  .spinner {
    flex: 1 1 auto;
    height: 100%;
    width: 100%;
  }

  .spinner__track,
  .spinner__indicator {
    fill: none;
    stroke-width: var(--track-width);
    r: calc(0.5em - var(--track-width) / 2);
    cx: 0.5em;
    cy: 0.5em;
    transform-origin: 50% 50%;
  }

  .spinner__track {
    stroke: var(--track-color);
    transform-origin: 0% 0%;
    mix-blend-mode: multiply;
  }

  .spinner__indicator {
    stroke: var(--indicator-color);
    stroke-linecap: round;
    stroke-dasharray: 150% 75%;
    animation: spin var(--speed) linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
      stroke-dasharray: 0.01em, 2.75em;
    }

    50% {
      transform: rotate(450deg);
      stroke-dasharray: 1.375em, 1.375em;
    }

    100% {
      transform: rotate(1080deg);
      stroke-dasharray: 0.01em, 2.75em;
    }
  }
`,Xo=class extends $e{render(){return se`
      <svg part="base" class="spinner" role="status">
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};Xo.styles=Jo,Xo=pt([Te("sl-spinner")],Xo);class Qo extends et{static styles=i`
    .plot {
        position: relative;
        height: 100%;
        width: 100%;
        grid-column-start: span 3;
    }
    .frame {
        height: 100%;
        width: 100%;
    }
    .loading {
        display: flex;
        justify-content: center;
        padding: 5% 0%;
        font-size: 15vw;
    }
  `;static properties={path:{type:String}};hideLoading(){this.renderRoot.querySelector("#loading").style.display="none"}render(){return z`
            <div id="loading" class="loading">
                <sl-spinner></sl-spinner>
            </div>
            <div class="plot">
                <iframe @load=${this.hideLoading} seamless frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
            </div>
        `}}customElements.define("diagram-element",Qo);class ts{}const es=new WeakMap,os=ho(class extends So{render(t){return L}update(t,[e]){var o;const s=e!==this.U;return s&&void 0!==this.U&&this.ot(void 0),(s||this.rt!==this.lt)&&(this.U=e,this.ht=null===(o=t.options)||void 0===o?void 0:o.host,this.ot(this.lt=t.element)),L}ot(t){var e;if("function"==typeof this.U){const o=null!==(e=this.ht)&&void 0!==e?e:globalThis;let s=es.get(o);void 0===s&&(s=new WeakMap,es.set(o,s)),void 0!==s.get(this.U)&&this.U.call(this.ht,void 0),s.set(this.U,t),void 0!==t&&this.U.call(this.ht,t)}else this.U.value=t}get rt(){var t,e,o;return"function"==typeof this.U?null===(e=es.get(null!==(t=this.ht)&&void 0!==t?t:globalThis))||void 0===e?void 0:e.get(this.U):null===(o=this.U)||void 0===o?void 0:o.value}disconnected(){this.rt===this.lt&&this.ot(void 0)}reconnected(){this.ot(this.lt)}});var ss=Mt`
  ${xe}

  :host {
    display: block;
  }

  .details {
    border: solid 1px var(--sl-color-neutral-200);
    border-radius: var(--sl-border-radius-medium);
    background-color: var(--sl-color-neutral-0);
    overflow-anchor: none;
  }

  .details--disabled {
    opacity: 0.5;
  }

  .details__header {
    display: flex;
    align-items: center;
    border-radius: inherit;
    padding: var(--sl-spacing-medium);
    user-select: none;
    cursor: pointer;
  }

  .details__header:focus {
    outline: none;
  }

  .details__header${Re} {
    outline: var(--sl-focus-ring);
    outline-offset: calc(1px + var(--sl-focus-ring-offset));
  }

  .details--disabled .details__header {
    cursor: not-allowed;
  }

  .details--disabled .details__header${Re} {
    outline: none;
    box-shadow: none;
  }

  .details__summary {
    flex: 1 1 auto;
    display: flex;
    align-items: center;
  }

  .details__summary-icon {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    transition: var(--sl-transition-medium) transform ease;
  }

  .details--open .details__summary-icon {
    transform: rotate(90deg);
  }

  .details__body {
    overflow: hidden;
  }

  .details__content {
    padding: var(--sl-spacing-medium);
  }
`,rs=class extends $e{constructor(){super(...arguments),this.open=!1,this.disabled=!1}firstUpdated(){this.body.hidden=!this.open,this.body.style.height=this.open?"auto":"0"}async show(){if(!this.open&&!this.disabled)return this.open=!0,ke(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,ke(this,"sl-after-hide")}handleSummaryClick(){this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){Ee(this,"sl-show"),await vt(this.body),this.body.hidden=!1;const{keyframes:t,options:e}=_t(this,"details.show");await bt(this.body,gt(t,this.body.scrollHeight),e),this.body.style.height="auto",Ee(this,"sl-after-show")}else{Ee(this,"sl-hide"),await vt(this.body);const{keyframes:t,options:e}=_t(this,"details.hide");await bt(this.body,gt(t,this.body.scrollHeight),e),this.body.hidden=!0,this.body.style.height="auto",Ee(this,"sl-after-hide")}}render(){return se`
      <div
        part="base"
        class=${Ae({details:!0,"details--open":this.open,"details--disabled":this.disabled})}
      >
        <header
          part="header"
          id="header"
          class="details__header"
          role="button"
          aria-expanded=${this.open?"true":"false"}
          aria-controls="content"
          aria-disabled=${this.disabled?"true":"false"}
          tabindex=${this.disabled?"-1":"0"}
          @click=${this.handleSummaryClick}
          @keydown=${this.handleSummaryKeyDown}
        >
          <div part="summary" class="details__summary">
            <slot name="summary">${this.summary}</slot>
          </div>

          <span part="summary-icon" class="details__summary-icon">
            <sl-icon name="chevron-right" library="system"></sl-icon>
          </span>
        </header>

        <div class="details__body">
          <div part="content" id="content" class="details__content" role="region" aria-labelledby="header">
            <slot></slot>
          </div>
        </div>
      </div>
    `}};rs.styles=ss,pt([ze(".details")],rs.prototype,"details",2),pt([ze(".details__header")],rs.prototype,"header",2),pt([ze(".details__body")],rs.prototype,"body",2),pt([Me({type:Boolean,reflect:!0})],rs.prototype,"open",2),pt([Me()],rs.prototype,"summary",2),pt([Me({type:Boolean,reflect:!0})],rs.prototype,"disabled",2),pt([Se("open",{waitUntilFirstUpdate:!0})],rs.prototype,"handleOpenChange",1),rs=pt([Te("sl-details")],rs),yt("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),yt("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}});var is=Mt`
  ${xe}

  :host {
    display: inline-block;
    position: relative;
    width: auto;
    cursor: pointer;
  }

  .button {
    display: inline-flex;
    align-items: stretch;
    justify-content: center;
    width: 100%;
    border-style: solid;
    border-width: var(--sl-input-border-width);
    font-family: var(--sl-input-font-family);
    font-weight: var(--sl-font-weight-semibold);
    text-decoration: none;
    user-select: none;
    white-space: nowrap;
    vertical-align: middle;
    padding: 0;
    transition: var(--sl-transition-x-fast) background-color, var(--sl-transition-x-fast) color,
      var(--sl-transition-x-fast) border, var(--sl-transition-x-fast) box-shadow;
    cursor: inherit;
  }

  .button::-moz-focus-inner {
    border: 0;
  }

  .button:focus {
    outline: none;
  }

  .button${Re} {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  .button--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* When disabled, prevent mouse events from bubbling up */
  .button--disabled * {
    pointer-events: none;
  }

  .button__prefix,
  .button__suffix {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    pointer-events: none;
  }

  .button__label ::slotted(sl-icon) {
    vertical-align: -2px;
  }

  /*
   * Standard buttons
   */

  /* Default */
  .button--standard.button--default {
    background-color: var(--sl-color-neutral-0);
    border-color: var(--sl-color-neutral-300);
    color: var(--sl-color-neutral-700);
  }

  .button--standard.button--default:hover:not(.button--disabled) {
    background-color: var(--sl-color-primary-50);
    border-color: var(--sl-color-primary-300);
    color: var(--sl-color-primary-700);
  }

  .button--standard.button--default:active:not(.button--disabled) {
    background-color: var(--sl-color-primary-100);
    border-color: var(--sl-color-primary-400);
    color: var(--sl-color-primary-700);
  }

  /* Primary */
  .button--standard.button--primary {
    background-color: var(--sl-color-primary-600);
    border-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--primary:hover:not(.button--disabled) {
    background-color: var(--sl-color-primary-500);
    border-color: var(--sl-color-primary-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--primary:active:not(.button--disabled) {
    background-color: var(--sl-color-primary-600);
    border-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  /* Success */
  .button--standard.button--success {
    background-color: var(--sl-color-success-600);
    border-color: var(--sl-color-success-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--success:hover:not(.button--disabled) {
    background-color: var(--sl-color-success-500);
    border-color: var(--sl-color-success-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--success:active:not(.button--disabled) {
    background-color: var(--sl-color-success-600);
    border-color: var(--sl-color-success-600);
    color: var(--sl-color-neutral-0);
  }

  /* Neutral */
  .button--standard.button--neutral {
    background-color: var(--sl-color-neutral-600);
    border-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--neutral:hover:not(.button--disabled) {
    background-color: var(--sl-color-neutral-500);
    border-color: var(--sl-color-neutral-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--neutral:active:not(.button--disabled) {
    background-color: var(--sl-color-neutral-600);
    border-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-0);
  }

  /* Warning */
  .button--standard.button--warning {
    background-color: var(--sl-color-warning-600);
    border-color: var(--sl-color-warning-600);
    color: var(--sl-color-neutral-0);
  }
  .button--standard.button--warning:hover:not(.button--disabled) {
    background-color: var(--sl-color-warning-500);
    border-color: var(--sl-color-warning-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--warning:active:not(.button--disabled) {
    background-color: var(--sl-color-warning-600);
    border-color: var(--sl-color-warning-600);
    color: var(--sl-color-neutral-0);
  }

  /* Danger */
  .button--standard.button--danger {
    background-color: var(--sl-color-danger-600);
    border-color: var(--sl-color-danger-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--danger:hover:not(.button--disabled) {
    background-color: var(--sl-color-danger-500);
    border-color: var(--sl-color-danger-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--danger:active:not(.button--disabled) {
    background-color: var(--sl-color-danger-600);
    border-color: var(--sl-color-danger-600);
    color: var(--sl-color-neutral-0);
  }

  /*
   * Outline buttons
   */

  .button--outline {
    background: none;
    border: solid 1px;
  }

  /* Default */
  .button--outline.button--default {
    border-color: var(--sl-color-neutral-300);
    color: var(--sl-color-neutral-700);
  }

  .button--outline.button--default:hover:not(.button--disabled),
  .button--outline.button--default.button--checked:not(.button--disabled) {
    border-color: var(--sl-color-primary-600);
    background-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--default:active:not(.button--disabled) {
    border-color: var(--sl-color-primary-700);
    background-color: var(--sl-color-primary-700);
    color: var(--sl-color-neutral-0);
  }

  /* Primary */
  .button--outline.button--primary {
    border-color: var(--sl-color-primary-600);
    color: var(--sl-color-primary-600);
  }

  .button--outline.button--primary:hover:not(.button--disabled),
  .button--outline.button--primary.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--primary:active:not(.button--disabled) {
    border-color: var(--sl-color-primary-700);
    background-color: var(--sl-color-primary-700);
    color: var(--sl-color-neutral-0);
  }

  /* Success */
  .button--outline.button--success {
    border-color: var(--sl-color-success-600);
    color: var(--sl-color-success-600);
  }

  .button--outline.button--success:hover:not(.button--disabled),
  .button--outline.button--success.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-success-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--success:active:not(.button--disabled) {
    border-color: var(--sl-color-success-700);
    background-color: var(--sl-color-success-700);
    color: var(--sl-color-neutral-0);
  }

  /* Neutral */
  .button--outline.button--neutral {
    border-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-600);
  }

  .button--outline.button--neutral:hover:not(.button--disabled),
  .button--outline.button--neutral.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--neutral:active:not(.button--disabled) {
    border-color: var(--sl-color-neutral-700);
    background-color: var(--sl-color-neutral-700);
    color: var(--sl-color-neutral-0);
  }

  /* Warning */
  .button--outline.button--warning {
    border-color: var(--sl-color-warning-600);
    color: var(--sl-color-warning-600);
  }

  .button--outline.button--warning:hover:not(.button--disabled),
  .button--outline.button--warning.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-warning-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--warning:active:not(.button--disabled) {
    border-color: var(--sl-color-warning-700);
    background-color: var(--sl-color-warning-700);
    color: var(--sl-color-neutral-0);
  }

  /* Danger */
  .button--outline.button--danger {
    border-color: var(--sl-color-danger-600);
    color: var(--sl-color-danger-600);
  }

  .button--outline.button--danger:hover:not(.button--disabled),
  .button--outline.button--danger.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-danger-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--danger:active:not(.button--disabled) {
    border-color: var(--sl-color-danger-700);
    background-color: var(--sl-color-danger-700);
    color: var(--sl-color-neutral-0);
  }

  /*
   * Text buttons
   */

  .button--text {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-600);
  }

  .button--text:hover:not(.button--disabled) {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-500);
  }

  .button--text${Re}:not(.button--disabled) {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-500);
  }

  .button--text:active:not(.button--disabled) {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-700);
  }

  /*
   * Size modifiers
   */

  .button--small {
    font-size: var(--sl-button-font-size-small);
    height: var(--sl-input-height-small);
    line-height: calc(var(--sl-input-height-small) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-small);
  }

  .button--medium {
    font-size: var(--sl-button-font-size-medium);
    height: var(--sl-input-height-medium);
    line-height: calc(var(--sl-input-height-medium) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-medium);
  }

  .button--large {
    font-size: var(--sl-button-font-size-large);
    height: var(--sl-input-height-large);
    line-height: calc(var(--sl-input-height-large) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-large);
  }

  /*
   * Pill modifier
   */

  .button--pill.button--small {
    border-radius: var(--sl-input-height-small);
  }

  .button--pill.button--medium {
    border-radius: var(--sl-input-height-medium);
  }

  .button--pill.button--large {
    border-radius: var(--sl-input-height-large);
  }

  /*
   * Circle modifier
   */

  .button--circle {
    padding-left: 0;
    padding-right: 0;
  }

  .button--circle.button--small {
    width: var(--sl-input-height-small);
    border-radius: 50%;
  }

  .button--circle.button--medium {
    width: var(--sl-input-height-medium);
    border-radius: 50%;
  }

  .button--circle.button--large {
    width: var(--sl-input-height-large);
    border-radius: 50%;
  }

  .button--circle .button__prefix,
  .button--circle .button__suffix,
  .button--circle .button__caret {
    display: none;
  }

  /*
   * Caret modifier
   */

  .button--caret .button__suffix {
    display: none;
  }

  .button--caret .button__caret {
    display: flex;
    align-items: center;
  }

  .button--caret .button__caret svg {
    width: 1em;
    height: 1em;
  }

  /*
   * Loading modifier
   */

  .button--loading {
    position: relative;
    cursor: wait;
  }

  .button--loading .button__prefix,
  .button--loading .button__label,
  .button--loading .button__suffix,
  .button--loading .button__caret {
    visibility: hidden;
  }

  .button--loading sl-spinner {
    --indicator-color: currentColor;
    position: absolute;
    font-size: 1em;
    height: 1em;
    width: 1em;
    top: calc(50% - 0.5em);
    left: calc(50% - 0.5em);
  }

  /*
   * Badges
   */

  .button ::slotted(sl-badge) {
    position: absolute;
    top: 0;
    right: 0;
    transform: translateY(-50%) translateX(50%);
    pointer-events: none;
  }

  /*
   * Button spacing
   */

  .button--has-label.button--small .button__label {
    padding: 0 var(--sl-spacing-small);
  }

  .button--has-label.button--medium .button__label {
    padding: 0 var(--sl-spacing-medium);
  }

  .button--has-label.button--large .button__label {
    padding: 0 var(--sl-spacing-large);
  }

  .button--has-prefix.button--small {
    padding-left: var(--sl-spacing-x-small);
  }

  .button--has-prefix.button--small .button__label {
    padding-left: var(--sl-spacing-x-small);
  }

  .button--has-prefix.button--medium {
    padding-left: var(--sl-spacing-small);
  }

  .button--has-prefix.button--medium .button__label {
    padding-left: var(--sl-spacing-small);
  }

  .button--has-prefix.button--large {
    padding-left: var(--sl-spacing-small);
  }

  .button--has-prefix.button--large .button__label {
    padding-left: var(--sl-spacing-small);
  }

  .button--has-suffix.button--small,
  .button--caret.button--small {
    padding-right: var(--sl-spacing-x-small);
  }

  .button--has-suffix.button--small .button__label,
  .button--caret.button--small .button__label {
    padding-right: var(--sl-spacing-x-small);
  }

  .button--has-suffix.button--medium,
  .button--caret.button--medium {
    padding-right: var(--sl-spacing-small);
  }

  .button--has-suffix.button--medium .button__label,
  .button--caret.button--medium .button__label {
    padding-right: var(--sl-spacing-small);
  }

  .button--has-suffix.button--large,
  .button--caret.button--large {
    padding-right: var(--sl-spacing-small);
  }

  .button--has-suffix.button--large .button__label,
  .button--caret.button--large .button__label {
    padding-right: var(--sl-spacing-small);
  }

  /*
   * Button groups support a variety of button types (e.g. buttons with tooltips, buttons as dropdown triggers, etc.).
   * This means buttons aren't always direct descendants of the button group, thus we can't target them with the
   * ::slotted selector. To work around this, the button group component does some magic to add these special classes to
   * buttons and we style them here instead.
   */

  :host(.sl-button-group__button--first:not(.sl-button-group__button--last)) .button {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }

  :host(.sl-button-group__button--inner) .button {
    border-radius: 0;
  }

  :host(.sl-button-group__button--last:not(.sl-button-group__button--first)) .button {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }

  /* All except the first */
  :host(.sl-button-group__button:not(.sl-button-group__button--first)) {
    margin-left: calc(-1 * var(--sl-input-border-width));
  }

  /* Add a visual separator between solid buttons */
  :host(.sl-button-group__button:not(.sl-button-group__button--focus, .sl-button-group__button--first, [variant='default']):not(:hover, :active, :focus))
    .button:after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    border-left: solid 1px rgb(128 128 128 / 33%);
    mix-blend-mode: multiply;
  }

  /* Bump hovered, focused, and checked buttons up so their focus ring isn't clipped */
  :host(.sl-button-group__button--hover) {
    z-index: 1;
  }

  :host(.sl-button-group__button--focus),
  :host(.sl-button-group__button[checked]) {
    z-index: 2;
  }
`,ns=class extends Event{constructor(t){super("formdata"),this.formData=t}},as=class extends FormData{constructor(t){var e=(...t)=>{super(...t)};t?(e(t),this.form=t,t.dispatchEvent(new ns(this))):e()}append(t,e){if(!this.form)return super.append(t,e);let o=this.form.elements[t];if(o||(o=document.createElement("input"),o.type="hidden",o.name=t,this.form.appendChild(o)),this.has(t)){const s=this.getAll(t),r=s.indexOf(o.value);-1!==r&&s.splice(r,1),s.push(e),this.set(t,s)}else super.append(t,e);o.value=e}};function ls(){window.FormData&&!function(){const t=document.createElement("form");let e=!1;return document.body.append(t),t.addEventListener("submit",(t=>{new FormData(t.target),t.preventDefault()})),t.addEventListener("formdata",(()=>e=!0)),t.dispatchEvent(new Event("submit",{cancelable:!0})),t.remove(),e}()&&(window.FormData=as,window.addEventListener("submit",(t=>{t.defaultPrevented||new FormData(t.target)})))}"complete"===document.readyState?ls():window.addEventListener("DOMContentLoaded",(()=>ls()));var cs=class extends $e{constructor(){super(...arguments),this.formSubmitController=new class{constructor(t,e){(this.host=t).addController(this),this.options=ht({form:t=>t.closest("form"),name:t=>t.name,value:t=>t.value,disabled:t=>t.disabled,reportValidity:t=>"function"!=typeof t.reportValidity||t.reportValidity()},e),this.handleFormData=this.handleFormData.bind(this),this.handleFormSubmit=this.handleFormSubmit.bind(this)}hostConnected(){this.form=this.options.form(this.host),this.form&&(this.form.addEventListener("formdata",this.handleFormData),this.form.addEventListener("submit",this.handleFormSubmit))}hostDisconnected(){this.form&&(this.form.removeEventListener("formdata",this.handleFormData),this.form.removeEventListener("submit",this.handleFormSubmit),this.form=void 0)}handleFormData(t){const e=this.options.disabled(this.host),o=this.options.name(this.host),s=this.options.value(this.host);e||"string"!=typeof o||void 0===s||(Array.isArray(s)?s.forEach((e=>{t.formData.append(o,e.toString())})):t.formData.append(o,s.toString()))}handleFormSubmit(t){const e=this.options.disabled(this.host),o=this.options.reportValidity;!this.form||this.form.noValidate||e||o(this.host)||(t.preventDefault(),t.stopImmediatePropagation())}submit(t){if(this.form){const e=document.createElement("button");e.type="submit",e.style.position="absolute",e.style.width="0",e.style.height="0",e.style.clipPath="inset(50%)",e.style.overflow="hidden",e.style.whiteSpace="nowrap",t&&["formaction","formmethod","formnovalidate","formtarget"].forEach((o=>{t.hasAttribute(o)&&e.setAttribute(o,t.getAttribute(o))})),this.form.append(e),e.click(),e.remove()}}}(this,{form:t=>{if(t.hasAttribute("form")){const e=t.getRootNode(),o=t.getAttribute("form");return e.getElementById(o)}return t.closest("form")}}),this.hasSlotController=new At(this,"[default]","prefix","suffix"),this.hasFocus=!1,this.variant="default",this.size="medium",this.caret=!1,this.disabled=!1,this.loading=!1,this.outline=!1,this.pill=!1,this.circle=!1,this.type="button"}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Ee(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Ee(this,"sl-focus")}handleClick(t){if(this.disabled||this.loading)return t.preventDefault(),void t.stopPropagation();"submit"===this.type&&this.formSubmitController.submit(this)}render(){const t=!!this.href,e=t?Fe`a`:Fe`button`;return Ve`
      <${e}
        part="base"
        class=${Ae({button:!0,"button--default":"default"===this.variant,"button--primary":"primary"===this.variant,"button--success":"success"===this.variant,"button--neutral":"neutral"===this.variant,"button--warning":"warning"===this.variant,"button--danger":"danger"===this.variant,"button--text":"text"===this.variant,"button--small":"small"===this.size,"button--medium":"medium"===this.size,"button--large":"large"===this.size,"button--caret":this.caret,"button--circle":this.circle,"button--disabled":this.disabled,"button--focused":this.hasFocus,"button--loading":this.loading,"button--standard":!this.outline,"button--outline":this.outline,"button--pill":this.pill,"button--has-label":this.hasSlotController.test("[default]"),"button--has-prefix":this.hasSlotController.test("prefix"),"button--has-suffix":this.hasSlotController.test("suffix")})}
        ?disabled=${qe(t?void 0:this.disabled)}
        type=${qe(t?void 0:this.type)}
        name=${qe(t?void 0:this.name)}
        value=${qe(t?void 0:this.value)}
        href=${qe(t?this.href:void 0)}
        target=${qe(t?this.target:void 0)}
        download=${qe(t?this.download:void 0)}
        rel=${qe(t&&this.target?"noreferrer noopener":void 0)}
        role=${qe(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <span part="prefix" class="button__prefix">
          <slot name="prefix"></slot>
        </span>
        <span part="label" class="button__label">
          <slot></slot>
        </span>
        <span part="suffix" class="button__suffix">
          <slot name="suffix"></slot>
        </span>
        ${this.caret?Ve`
                <span part="caret" class="button__caret">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </span>
              `:""}
        ${this.loading?Ve`<sl-spinner></sl-spinner>`:""}
      </${e}>
    `}};cs.styles=is,pt([ze(".button")],cs.prototype,"button",2),pt([Pe()],cs.prototype,"hasFocus",2),pt([Me({reflect:!0})],cs.prototype,"variant",2),pt([Me({reflect:!0})],cs.prototype,"size",2),pt([Me({type:Boolean,reflect:!0})],cs.prototype,"caret",2),pt([Me({type:Boolean,reflect:!0})],cs.prototype,"disabled",2),pt([Me({type:Boolean,reflect:!0})],cs.prototype,"loading",2),pt([Me({type:Boolean,reflect:!0})],cs.prototype,"outline",2),pt([Me({type:Boolean,reflect:!0})],cs.prototype,"pill",2),pt([Me({type:Boolean,reflect:!0})],cs.prototype,"circle",2),pt([Me()],cs.prototype,"type",2),pt([Me()],cs.prototype,"name",2),pt([Me()],cs.prototype,"value",2),pt([Me()],cs.prototype,"href",2),pt([Me()],cs.prototype,"target",2),pt([Me()],cs.prototype,"download",2),pt([Me()],cs.prototype,"form",2),pt([Me({attribute:"formaction"})],cs.prototype,"formAction",2),pt([Me({attribute:"formmethod"})],cs.prototype,"formMethod",2),pt([Me({attribute:"formnovalidate",type:Boolean})],cs.prototype,"formNoValidate",2),pt([Me({attribute:"formtarget"})],cs.prototype,"formTarget",2),cs=pt([Te("sl-button")],cs);class ds extends Po{static styles=[Po.styles,i`
        sl-details::part(base) {
            max-width: 30vw;
            font-family: Arial, sans-serif;
            background-color: transparent;
            border: none;
        }
        sl-details::part(header) {
            font-weight: "bold";
            padding: var(--sl-spacing-x-small) var(--sl-spacing-4x-large) var(--sl-spacing-x-small) var(--sl-spacing-x-small);
            font-size: 12px;
        }
        `];tableRef=(()=>new ts)();removeDetailsEl(t){for(const e of t.childNodes)if("TR"===e.tagName)for(const t of e.childNodes)for(const e of t.childNodes)"SL-DETAILS"===e.tagName&&t.removeChild(e);return t}copyTable(){const t=window.getSelection();t.removeAllRanges();const e=document.createRange();e.selectNodeContents(this.tableRef.value),t.addRange(e),this.removeDetailsEl(t.anchorNode),document.execCommand("copy"),t.removeAllRanges(),this.requestUpdate()}parseMetric(t){const e=t[0].split("|");return z`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,o]=t.split("|");return z`
            <td class="td-value">
                ${o?z`<abbr title=${o}>${e}</abbr>`:z`${e}`}
            </td>
        `}async parseSrc(){let t,e=z``;for await(const o of this.makeTextFileLineIterator(this.src)){const s=o.split(";"),r=s[0];if(s.shift(),"H"===r)for(const t of s)e=z`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===r)t=this.parseMetric(s);else{const o=z`${s.map((t=>this.parseSummaryFunc(t)))}`;e=z`
                    ${e}
                    <tr>
                      ${t}
                      ${o}
                    </tr>
                `,t&&(t=void 0)}}return e=z`<table ${os(this.tableRef)} width=${this.getWidth(this.cols)}>${e}</table>`,z`
            <div style="display:flex;">
                ${e}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}}customElements.define("smry-tbl",ds);class hs extends Zo{static styles=i`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},smrytblpath:{type:String}};visibleTemplate(){return z`
            <br>
            ${this.smrytblpath?z`<smry-tbl .src="${this.smrytblpath}"></smry-tbl>`:z``}
            <div class="grid">
                ${this.paths.map((t=>z`
                    <diagram-element path="${t}"></diagram-element>
                `))}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",hs);class us extends et{static styles=i`
        /*
         * By default, inactive Shoelace tabs have 'display: none' which breaks Plotly legends.
         * Therefore we make inactive tabs invisible in our own way using the following two css
         * classes:
         */
        sl-tab-panel{
            display: block !important;
            height: 0px !important;
            overflow: hidden;
        }

        sl-tab-panel[active] {
            display: block !important;
            height: auto !important;
        }

        /*
         * The hierarchy of tabs can go up to and beyond 5 levels of depth. Remove the padding on
         * tab panels so that there is no space between each level of tabs.
         */
        .tab-panel::part(base) {
            padding: 0px 0px;
        }
        /*
         * Also reduce the bottom padding of tabs as it makes them easier to read.
         */
        .tab::part(base) {
            padding-bottom: var(--sl-spacing-x-small);
            font-family: Arial, sans-serif;
        }
    `;static properties={tabFile:{type:String},tabs:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};updated(t){t.has("tabFile")&&fetch(this.tabFile).then((t=>t.json())).then((t=>{this.tabs=t}))}tabTemplate(t){return t.tabs?z`
                <sl-tab-group>
                    ${t.tabs.map((t=>z`
                        <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                        <sl-tab-panel class="tab-panel" id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                    `))}
                </sl-tab-group>
        `:z`
            <wult-metric-tab tabname=${t.name} .smrytblpath=${t.smrytblpath} .paths=${t.ppaths} .dir=${t.dir}></wult-metric-tab>
        `}render(){return this.tabs?z`
            <sl-tab-group>
                ${this.tabs.map((t=>z`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
      `:z``}}customElements.define("tab-group",us);class ps extends et{static properties={src:{type:String},reportInfo:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};static styles=i`
        .report-head {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .report-title {
            font-family: Arial, sans-serif;
        }
    `;async connectedCallback(){super.connectedCallback();try{const t=await fetch(this.src);this.reportInfo=await t.json(),this.toolname=this.reportInfo.toolname,this.titleDescr=this.reportInfo.title_descr,this.tabFile=this.reportInfo.tab_file,this.introtbl=this.reportInfo.intro_tbl}catch(t){t instanceof TypeError&&(this.fetchFailed=!0)}}corsWarning(){return z`
        <sl-alert variant="danger" open>
          Warning: it looks like you might be trying to view this report
          locally.  See our documentation on how to do that <a
          href="https://intel.github.io/wult/pages/howto.html#open-wult-reports-locally">
            here.</a>
          </sl-alert>
      `}render(){return this.fetchFailed?this.corsWarning():z`
            <div class="report-head">
                <h1 class="report-title">${this.toolname} report</h1>
                ${this.titleDescr?z`
                    <p class="title_descr">${this.titleDescr}</p>
                    <br>
                    `:z``}

                <intro-tbl .src=${this.introtbl}></intro-tbl>
            </div>
            <br>
            <tab-group .tabFile="${this.tabFile}"></tab-group>
        `}}customElements.define("report-page",ps),Ye("shoelace")})();