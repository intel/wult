/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),s=new Map;class o{constructor(t,s){if(this._$cssResult$=!0,s!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=s.get(this.cssText);return t&&void 0===e&&(s.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const i=t=>new o("string"==typeof t?t:t+"",e),r=(t,...s)=>{const i=1===t.length?t[0]:s.reduce(((e,s,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[o+1]),t[0]);return new o(i,e)},n=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return i(e)})(t):t;var a;const l=window.trustedTypes,c=l?l.emptyScript:"",d=window.reactiveElementPolyfillSupport,h={toAttribute(t,e){switch(e){case Boolean:t=t?c:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},u=(t,e)=>e!==t&&(e==e||t==t),p={attribute:!0,type:String,converter:h,reflect:!1,hasChanged:u};class b extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const o=this._$Eh(s,e);void 0!==o&&(this._$Eu.set(o,s),t.push(o))})),t}static createProperty(t,e=p){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,o=this.getPropertyDescriptor(t,s,e);void 0!==o&&Object.defineProperty(this.prototype,t,o)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(o){const i=this[t];this[e]=o,this.requestUpdate(t,i,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||p}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const s=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{t?e.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const s=document.createElement("style"),o=window.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=t.cssText,e.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=p){var o,i;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(i=null===(o=s.converter)||void 0===o?void 0:o.toAttribute)&&void 0!==i?i:h.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,o,i;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),a=t.converter,l=null!==(i=null!==(o=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==o?o:"function"==typeof a?a:null)&&void 0!==i?i:h.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let o=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||u)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,s))):o=!1),!this.isUpdatePending&&o&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var v;b.finalized=!0,b.elementProperties=new Map,b.elementStyles=[],b.shadowRootOptions={mode:"open"},null==d||d({ReactiveElement:b}),(null!==(a=globalThis.reactiveElementVersions)&&void 0!==a?a:globalThis.reactiveElementVersions=[]).push("1.3.2");const f=globalThis.trustedTypes,g=f?f.createPolicy("lit-html",{createHTML:t=>t}):void 0,m=`lit$${(Math.random()+"").slice(9)}$`,y="?"+m,_=`<${y}>`,$=document,w=(t="")=>$.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,x=Array.isArray,C=t=>{var e;return x(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,E=/-->/g,k=/>/g,T=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,U=/'/g,P=/"/g,M=/^(?:script|style|textarea|title)$/i,N=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),H=N(1),z=(N(2),Symbol.for("lit-noChange")),O=Symbol.for("lit-nothing"),L=new WeakMap,B=(t,e,s)=>{var o,i;const r=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:e;let n=r._$litPart$;if(void 0===n){const t=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:null;r._$litPart$=n=new W(e.insertBefore(w(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n},R=$.createTreeWalker($,129,null,!1),D=(t,e)=>{const s=t.length-1,o=[];let i,r=2===e?"<svg>":"",n=S;for(let e=0;e<s;e++){const s=t[e];let a,l,c=-1,d=0;for(;d<s.length&&(n.lastIndex=d,l=n.exec(s),null!==l);)d=n.lastIndex,n===S?"!--"===l[1]?n=E:void 0!==l[1]?n=k:void 0!==l[2]?(M.test(l[2])&&(i=RegExp("</"+l[2],"g")),n=T):void 0!==l[3]&&(n=T):n===T?">"===l[0]?(n=null!=i?i:S,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?T:'"'===l[3]?P:U):n===P||n===U?n=T:n===E||n===k?n=S:(n=T,i=void 0);const h=n===T&&t[e+1].startsWith("/>")?" ":"";r+=n===S?s+_:c>=0?(o.push(a),s.slice(0,c)+"$lit$"+s.slice(c)+m+h):s+m+(-2===c?(o.push(void 0),e):h)}const a=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==g?g.createHTML(a):a,o]};class I{constructor({strings:t,_$litType$:e},s){let o;this.parts=[];let i=0,r=0;const n=t.length-1,a=this.parts,[l,c]=D(t,e);if(this.el=I.createElement(l,s),R.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(o=R.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes()){const t=[];for(const e of o.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(m)){const s=c[r++];if(t.push(e),void 0!==s){const t=o.getAttribute(s.toLowerCase()+"$lit$").split(m),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:i,name:e[2],strings:t,ctor:"."===e[1]?q:"?"===e[1]?G:"@"===e[1]?Y:V})}else a.push({type:6,index:i})}for(const e of t)o.removeAttribute(e)}if(M.test(o.tagName)){const t=o.textContent.split(m),e=t.length-1;if(e>0){o.textContent=f?f.emptyScript:"";for(let s=0;s<e;s++)o.append(t[s],w()),R.nextNode(),a.push({type:2,index:++i});o.append(t[e],w())}}}else if(8===o.nodeType)if(o.data===y)a.push({type:2,index:i});else{let t=-1;for(;-1!==(t=o.data.indexOf(m,t+1));)a.push({type:7,index:i}),t+=m.length-1}i++}}static createElement(t,e){const s=$.createElement("template");return s.innerHTML=t,s}}function F(t,e,s=t,o){var i,r,n,a;if(e===z)return e;let l=void 0!==o?null===(i=s._$Cl)||void 0===i?void 0:i[o]:s._$Cu;const c=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==c&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===c?l=void 0:(l=new c(t),l._$AT(t,s,o)),void 0!==o?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[o]=l:s._$Cu=l),void 0!==l&&(e=F(t,l._$AS(t,e.values),l,o)),e}class j{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:o}=this._$AD,i=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:$).importNode(s,!0);R.currentNode=i;let r=R.nextNode(),n=0,a=0,l=o[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new W(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new Z(r,this,t)),this.v.push(e),l=o[++a]}n!==(null==l?void 0:l.index)&&(r=R.nextNode(),n++)}return i}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class W{constructor(t,e,s,o){var i;this.type=2,this._$AH=O,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=o,this._$Cg=null===(i=null==o?void 0:o.isConnected)||void 0===i||i}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=F(this,t,e),A(t)?t===O||null==t||""===t?(this._$AH!==O&&this._$AR(),this._$AH=O):t!==this._$AH&&t!==z&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):C(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==O&&A(this._$AH)?this._$AA.nextSibling.data=t:this.k($.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:o}=t,i="number"==typeof o?this._$AC(t):(void 0===o.el&&(o.el=I.createElement(o.h,this.options)),o);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===i)this._$AH.m(s);else{const t=new j(i,this),e=t.p(this.options);t.m(s),this.k(e),this._$AH=t}}_$AC(t){let e=L.get(t.strings);return void 0===e&&L.set(t.strings,e=new I(t)),e}S(t){x(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,o=0;for(const i of t)o===e.length?e.push(s=new W(this.M(w()),this.M(w()),this,this.options)):s=e[o],s._$AI(i),o++;o<e.length&&(this._$AR(s&&s._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class V{constructor(t,e,s,o,i){this.type=1,this._$AH=O,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=i,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=O}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,o){const i=this.strings;let r=!1;if(void 0===i)t=F(this,t,e,0),r=!A(t)||t!==this._$AH&&t!==z,r&&(this._$AH=t);else{const o=t;let n,a;for(t=i[0],n=0;n<i.length-1;n++)a=F(this,o[s+n],e,n),a===z&&(a=this._$AH[n]),r||(r=!A(a)||a!==this._$AH[n]),a===O?t=O:t!==O&&(t+=(null!=a?a:"")+i[n+1]),this._$AH[n]=a}r&&!o&&this.C(t)}C(t){t===O?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class q extends V{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===O?void 0:t}}const K=f?f.emptyScript:"";class G extends V{constructor(){super(...arguments),this.type=4}C(t){t&&t!==O?this.element.setAttribute(this.name,K):this.element.removeAttribute(this.name)}}class Y extends V{constructor(t,e,s,o,i){super(t,e,s,o,i),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=F(this,t,e,0))&&void 0!==s?s:O)===z)return;const o=this._$AH,i=t===O&&o!==O||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==O&&(o===O||i);i&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}}class Z{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){F(this,t)}}const J={L:"$lit$",P:m,V:y,I:1,N:D,R:j,j:C,D:F,H:W,F:V,O:G,W:Y,B:q,Z},X=window.litHtmlPolyfillSupport;var Q,tt;null==X||X(I,W),(null!==(v=globalThis.litHtmlVersions)&&void 0!==v?v:globalThis.litHtmlVersions=[]).push("2.2.5");class et extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=B(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return z}}et.finalized=!0,et._$litElement$=!0,null===(Q=globalThis.litElementHydrateSupport)||void 0===Q||Q.call(globalThis,{LitElement:et});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:et}),(null!==(tt=globalThis.litElementVersions)&&void 0!==tt?tt:globalThis.litElementVersions=[]).push("3.2.0"),Object.create;var ot=Object.defineProperty,it=Object.defineProperties,rt=Object.getOwnPropertyDescriptor,nt=Object.getOwnPropertyDescriptors,at=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),lt=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),ct=Object.prototype.propertyIsEnumerable,dt=(t,e,s)=>e in t?ot(t,e,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[e]=s,ht=(t,e)=>{for(var s in e||(e={}))lt.call(e,s)&&dt(t,s,e[s]);if(at)for(var s of at(e))ct.call(e,s)&&dt(t,s,e[s]);return t},ut=(t,e)=>it(t,nt(e)),pt=(t,e,s,o)=>{for(var i,r=o>1?void 0:o?rt(e,s):e,n=t.length-1;n>=0;n--)(i=t[n])&&(r=(o?i(e,s,r):i(r))||r);return o&&r&&ot(e,s,r),r};function bt(t,e,s){return new Promise((o=>{if((null==s?void 0:s.duration)===1/0)throw new Error("Promise-based animations must be finite.");const i=t.animate(e,ut(ht({},s),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:s.duration}));i.addEventListener("cancel",o,{once:!0}),i.addEventListener("finish",o,{once:!0})}))}function vt(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const s=requestAnimationFrame(e);t.addEventListener("cancel",(()=>s),{once:!0}),t.addEventListener("finish",(()=>s),{once:!0}),t.cancel()})))))}function ft(t,e){return t.map((t=>ut(ht({},t),{height:"auto"===t.height?`${e}px`:t.height})))}var gt=new Map,mt=new WeakMap;function yt(t,e){gt.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function _t(t,e){const s=mt.get(t);if(null==s?void 0:s[e])return s[e];return gt.get(e)||{keyframes:[],options:{duration:0}}}var $t,wt,At=class{constructor(t,...e){this.slotNames=[],(this.host=t).addController(this),this.slotNames=e,this.handleSlotChange=this.handleSlotChange.bind(this)}hasDefaultSlot(){return[...this.host.childNodes].some((t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1}))}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}handleSlotChange(t){const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()}},xt=t=>(...e)=>({_$litDirective$:t,values:e}),Ct=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},St=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Et=Symbol(),kt=new Map,Tt=class{constructor(t,e){if(this._$cssResult$=!0,e!==Et)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=kt.get(this.cssText);return St&&void 0===t&&(kt.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},Ut=t=>new Tt("string"==typeof t?t:t+"",Et),Pt=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,s,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[o+1]),t[0]);return new Tt(s,Et)},Mt=St?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return Ut(e)})(t):t,Nt=window.trustedTypes,Ht=Nt?Nt.emptyScript:"",zt=window.reactiveElementPolyfillSupport,Ot={toAttribute(t,e){switch(e){case Boolean:t=t?Ht:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},Lt=(t,e)=>e!==t&&(e==e||t==t),Bt={attribute:!0,type:String,converter:Ot,reflect:!1,hasChanged:Lt},Rt=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const o=this._$Eh(s,e);void 0!==o&&(this._$Eu.set(o,s),t.push(o))})),t}static createProperty(t,e=Bt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,o=this.getPropertyDescriptor(t,s,e);void 0!==o&&Object.defineProperty(this.prototype,t,o)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(o){const i=this[t];this[e]=o,this.requestUpdate(t,i,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Bt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(Mt(t))}else void 0!==t&&e.push(Mt(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,o=this.constructor.elementStyles,St?s.adoptedStyleSheets=o.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):o.forEach((t=>{const e=document.createElement("style"),o=window.litNonce;void 0!==o&&e.setAttribute("nonce",o),e.textContent=t.cssText,s.appendChild(e)})),e;var s,o}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=Bt){var o,i;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(i=null===(o=s.converter)||void 0===o?void 0:o.toAttribute)&&void 0!==i?i:Ot.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,o,i;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),a=t.converter,l=null!==(i=null!==(o=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==o?o:"function"==typeof a?a:null)&&void 0!==i?i:Ot.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let o=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||Lt)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,s))):o=!1),!this.isUpdatePending&&o&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}};Rt.finalized=!0,Rt.elementProperties=new Map,Rt.elementStyles=[],Rt.shadowRootOptions={mode:"open"},null==zt||zt({ReactiveElement:Rt}),(null!==($t=globalThis.reactiveElementVersions)&&void 0!==$t?$t:globalThis.reactiveElementVersions=[]).push("1.3.2");var Dt=globalThis.trustedTypes,It=Dt?Dt.createPolicy("lit-html",{createHTML:t=>t}):void 0,Ft=`lit$${(Math.random()+"").slice(9)}$`,jt="?"+Ft,Wt=`<${jt}>`,Vt=document,qt=(t="")=>Vt.createComment(t),Kt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Gt=Array.isArray,Yt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Zt=/-->/g,Jt=/>/g,Xt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,Qt=/'/g,te=/"/g,ee=/^(?:script|style|textarea|title)$/i,se=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),oe=se(1),ie=se(2),re=Symbol.for("lit-noChange"),ne=Symbol.for("lit-nothing"),ae=new WeakMap,le=Vt.createTreeWalker(Vt,129,null,!1),ce=class{constructor({strings:t,_$litType$:e},s){let o;this.parts=[];let i=0,r=0;const n=t.length-1,a=this.parts,[l,c]=((t,e)=>{const s=t.length-1,o=[];let i,r=2===e?"<svg>":"",n=Yt;for(let e=0;e<s;e++){const s=t[e];let a,l,c=-1,d=0;for(;d<s.length&&(n.lastIndex=d,l=n.exec(s),null!==l);)d=n.lastIndex,n===Yt?"!--"===l[1]?n=Zt:void 0!==l[1]?n=Jt:void 0!==l[2]?(ee.test(l[2])&&(i=RegExp("</"+l[2],"g")),n=Xt):void 0!==l[3]&&(n=Xt):n===Xt?">"===l[0]?(n=null!=i?i:Yt,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Xt:'"'===l[3]?te:Qt):n===te||n===Qt?n=Xt:n===Zt||n===Jt?n=Yt:(n=Xt,i=void 0);const h=n===Xt&&t[e+1].startsWith("/>")?" ":"";r+=n===Yt?s+Wt:c>=0?(o.push(a),s.slice(0,c)+"$lit$"+s.slice(c)+Ft+h):s+Ft+(-2===c?(o.push(void 0),e):h)}const a=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==It?It.createHTML(a):a,o]})(t,e);if(this.el=ce.createElement(l,s),le.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(o=le.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes()){const t=[];for(const e of o.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(Ft)){const s=c[r++];if(t.push(e),void 0!==s){const t=o.getAttribute(s.toLowerCase()+"$lit$").split(Ft),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:i,name:e[2],strings:t,ctor:"."===e[1]?ve:"?"===e[1]?ge:"@"===e[1]?me:be})}else a.push({type:6,index:i})}for(const e of t)o.removeAttribute(e)}if(ee.test(o.tagName)){const t=o.textContent.split(Ft),e=t.length-1;if(e>0){o.textContent=Dt?Dt.emptyScript:"";for(let s=0;s<e;s++)o.append(t[s],qt()),le.nextNode(),a.push({type:2,index:++i});o.append(t[e],qt())}}}else if(8===o.nodeType)if(o.data===jt)a.push({type:2,index:i});else{let t=-1;for(;-1!==(t=o.data.indexOf(Ft,t+1));)a.push({type:7,index:i}),t+=Ft.length-1}i++}}static createElement(t,e){const s=Vt.createElement("template");return s.innerHTML=t,s}};function de(t,e,s=t,o){var i,r,n,a;if(e===re)return e;let l=void 0!==o?null===(i=s._$Cl)||void 0===i?void 0:i[o]:s._$Cu;const c=Kt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==c&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===c?l=void 0:(l=new c(t),l._$AT(t,s,o)),void 0!==o?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[o]=l:s._$Cu=l),void 0!==l&&(e=de(t,l._$AS(t,e.values),l,o)),e}var he,ue,pe=class{constructor(t,e,s,o){var i;this.type=2,this._$AH=ne,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=o,this._$Cg=null===(i=null==o?void 0:o.isConnected)||void 0===i||i}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=de(this,t,e),Kt(t)?t===ne||null==t||""===t?(this._$AH!==ne&&this._$AR(),this._$AH=ne):t!==this._$AH&&t!==re&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):(t=>{var e;return Gt(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==ne&&Kt(this._$AH)?this._$AA.nextSibling.data=t:this.k(Vt.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:o}=t,i="number"==typeof o?this._$AC(t):(void 0===o.el&&(o.el=ce.createElement(o.h,this.options)),o);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===i)this._$AH.m(s);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:o}=this._$AD,i=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Vt).importNode(s,!0);le.currentNode=i;let r=le.nextNode(),n=0,a=0,l=o[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new pe(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new ye(r,this,t)),this.v.push(e),l=o[++a]}n!==(null==l?void 0:l.index)&&(r=le.nextNode(),n++)}return i}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}(i,this),e=t.p(this.options);t.m(s),this.k(e),this._$AH=t}}_$AC(t){let e=ae.get(t.strings);return void 0===e&&ae.set(t.strings,e=new ce(t)),e}S(t){Gt(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,o=0;for(const i of t)o===e.length?e.push(s=new pe(this.M(qt()),this.M(qt()),this,this.options)):s=e[o],s._$AI(i),o++;o<e.length&&(this._$AR(s&&s._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},be=class{constructor(t,e,s,o,i){this.type=1,this._$AH=ne,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=i,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=ne}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,o){const i=this.strings;let r=!1;if(void 0===i)t=de(this,t,e,0),r=!Kt(t)||t!==this._$AH&&t!==re,r&&(this._$AH=t);else{const o=t;let n,a;for(t=i[0],n=0;n<i.length-1;n++)a=de(this,o[s+n],e,n),a===re&&(a=this._$AH[n]),r||(r=!Kt(a)||a!==this._$AH[n]),a===ne?t=ne:t!==ne&&(t+=(null!=a?a:"")+i[n+1]),this._$AH[n]=a}r&&!o&&this.C(t)}C(t){t===ne?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},ve=class extends be{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===ne?void 0:t}},fe=Dt?Dt.emptyScript:"",ge=class extends be{constructor(){super(...arguments),this.type=4}C(t){t&&t!==ne?this.element.setAttribute(this.name,fe):this.element.removeAttribute(this.name)}},me=class extends be{constructor(t,e,s,o,i){super(t,e,s,o,i),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=de(this,t,e,0))&&void 0!==s?s:ne)===re)return;const o=this._$AH,i=t===ne&&o!==ne||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==ne&&(o===ne||i);i&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}},ye=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){de(this,t)}},_e=window.litHtmlPolyfillSupport;null==_e||_e(ce,pe),(null!==(wt=globalThis.litHtmlVersions)&&void 0!==wt?wt:globalThis.litHtmlVersions=[]).push("2.2.4");var $e=class extends Rt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,s)=>{var o,i;const r=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:e;let n=r._$litPart$;if(void 0===n){const t=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:null;r._$litPart$=n=new pe(e.insertBefore(qt(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return re}};$e.finalized=!0,$e._$litElement$=!0,null===(he=globalThis.litElementHydrateSupport)||void 0===he||he.call(globalThis,{LitElement:$e});var we=globalThis.litElementPolyfillSupport;null==we||we({LitElement:$e}),(null!==(ue=globalThis.litElementVersions)&&void 0!==ue?ue:globalThis.litElementVersions=[]).push("3.2.0");var Ae=xt(class extends Ct{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var s,o;if(void 0===this.et){this.et=new Set,void 0!==t.strings&&(this.st=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(s=this.st)||void 0===s?void 0:s.has(t))&&this.et.add(t);return this.render(e)}const i=t.element.classList;this.et.forEach((t=>{t in e||(i.remove(t),this.et.delete(t))}));for(const t in e){const s=!!e[t];s===this.et.has(t)||(null===(o=this.st)||void 0===o?void 0:o.has(t))||(s?(i.add(t),this.et.add(t)):(i.remove(t),this.et.delete(t)))}return re}}),xe=Pt`
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
`,Ce=Pt`
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
`;function Se(t,e){const s=ht({waitUntilFirstUpdate:!1},e);return(e,o)=>{const{update:i}=e;if(t in e){const r=t;e.update=function(t){if(t.has(r)){const e=t.get(r),i=this[r];e!==i&&(s.waitUntilFirstUpdate&&!this.hasUpdated||this[o](e,i))}i.call(this,t)}}}}function Ee(t,e,s){const o=new CustomEvent(e,ht({bubbles:!0,cancelable:!1,composed:!0,detail:{}},s));return t.dispatchEvent(o),o}function ke(t,e){return new Promise((s=>{t.addEventListener(e,(function o(i){i.target===t&&(t.removeEventListener(e,o),s())}))}))}var Te=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:s,elements:o}=e;return{kind:s,elements:o,finisher(e){window.customElements.define(t,e)}}})(t,e),Ue=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?ut(ht({},e),{finisher(s){s.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(s){s.createProperty(e.key,t)}};function Pe(t){return(e,s)=>void 0!==s?((t,e,s)=>{e.constructor.createProperty(s,t)})(t,e,s):Ue(t,e)}function Me(t){return Pe(ut(ht({},t),{state:!0}))}var Ne;function He(t,e){return(({finisher:t,descriptor:e})=>(s,o)=>{var i;if(void 0===o){const o=null!==(i=s.originalKey)&&void 0!==i?i:s.key,r=null!=e?{kind:"method",placement:"prototype",key:o,descriptor:e(s.key)}:ut(ht({},s),{key:o});return null!=t&&(r.finisher=function(e){t(e,o)}),r}{const i=s.constructor;void 0!==e&&Object.defineProperty(s,o,e(o)),null==t||t(i,o)}})({descriptor:s=>{const o={get(){var e,s;return null!==(s=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==s?s:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof s?Symbol():"__"+s;o.get=function(){var s,o;return void 0===this[e]&&(this[e]=null!==(o=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(t))&&void 0!==o?o:null),this[e]}}return o}})}null===(Ne=window.HTMLSlotElement)||void 0===Ne||Ne.prototype.assignedElements;var ze=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Oe=class extends $e{constructor(){super(...arguments),this.hasSlotController=new At(this,"icon","suffix"),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,ke(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,ke(this,"sl-after-hide")}async toast(){return new Promise((t=>{null===ze.parentElement&&document.body.append(ze),ze.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{ze.removeChild(this),t(),null===ze.querySelector("sl-alert")&&ze.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){Ee(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await vt(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=_t(this,"alert.show");await bt(this.base,t,e),Ee(this,"sl-after-show")}else{Ee(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await vt(this.base);const{keyframes:t,options:e}=_t(this,"alert.hide");await bt(this.base,t,e),this.base.hidden=!0,Ee(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return oe`
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

        ${this.closable?oe`
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
    `}};Oe.styles=Ce,pt([He('[part="base"]')],Oe.prototype,"base",2),pt([Pe({type:Boolean,reflect:!0})],Oe.prototype,"open",2),pt([Pe({type:Boolean,reflect:!0})],Oe.prototype,"closable",2),pt([Pe({reflect:!0})],Oe.prototype,"variant",2),pt([Pe({type:Number})],Oe.prototype,"duration",2),pt([Se("open",{waitUntilFirstUpdate:!0})],Oe.prototype,"handleOpenChange",1),pt([Se("duration")],Oe.prototype,"handleDurationChange",1),Oe=pt([Te("sl-alert")],Oe),yt("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),yt("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var Le=(()=>{const t=document.createElement("style");let e;try{document.head.appendChild(t),t.sheet.insertRule(":focus-visible { color: inherit }"),e=!0}catch(t){e=!1}finally{t.remove()}return e})(),Be=Ut(Le?":focus-visible":":focus"),Re=Pt`
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

  .icon-button${Be} {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }
`,De=Symbol.for(""),Ie=t=>{var e,s;if((null===(e=t)||void 0===e?void 0:e.r)===De)return null===(s=t)||void 0===s?void 0:s._$litStatic$},Fe=(t,...e)=>({_$litStatic$:e.reduce(((e,s,o)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(s)+t[o+1]),t[0]),r:De}),je=new Map,We=t=>(e,...s)=>{const o=s.length;let i,r;const n=[],a=[];let l,c=0,d=!1;for(;c<o;){for(l=e[c];c<o&&void 0!==(r=s[c],i=Ie(r));)l+=i+e[++c],d=!0;a.push(r),n.push(l),c++}if(c===o&&n.push(e[o]),d){const t=n.join("$$lit$$");void 0===(e=je.get(t))&&(n.raw=n,je.set(t,e=n)),s=a}return t(e,...s)},Ve=We(oe),qe=(We(ie),t=>null!=t?t:ne),Ke=class extends $e{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Ee(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Ee(this,"sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}render(){const t=!!this.href,e=t?Fe`a`:Fe`button`;return Ve`
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
    `}};Ke.styles=Re,pt([Me()],Ke.prototype,"hasFocus",2),pt([He(".icon-button")],Ke.prototype,"button",2),pt([Pe()],Ke.prototype,"name",2),pt([Pe()],Ke.prototype,"library",2),pt([Pe()],Ke.prototype,"src",2),pt([Pe()],Ke.prototype,"href",2),pt([Pe()],Ke.prototype,"target",2),pt([Pe()],Ke.prototype,"download",2),pt([Pe()],Ke.prototype,"label",2),pt([Pe({type:Boolean,reflect:!0})],Ke.prototype,"disabled",2),Ke=pt([Te("sl-icon-button")],Ke);var Ge="";function Ye(t){Ge=t}var Ze=[...document.getElementsByTagName("script")],Je=Ze.find((t=>t.hasAttribute("data-shoelace")));if(Je)Ye(Je.getAttribute("data-shoelace"));else{const t=Ze.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let e="";t&&(e=t.getAttribute("src")),Ye(e.split("/").slice(0,-1).join("/"))}var Xe={"check-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">\n      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"></path>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},Qe=[{name:"default",resolver:t=>`${Ge.replace(/\/$/,"")}/assets/icons/${t}.svg`},{name:"system",resolver:t=>t in Xe?`data:image/svg+xml,${encodeURIComponent(Xe[t])}`:""}],ts=[];function es(t){return Qe.find((e=>e.name===t))}var ss=new Map,os=new Map;var is=Pt`
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
`,rs=class extends Ct{constructor(t){if(super(t),this.it=ne,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===ne||null==t)return this.ft=void 0,this.it=t;if(t===re)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.ft;this.it=t;const e=[t];return e.raw=e,this.ft={_$litType$:this.constructor.resultType,strings:e,values:[]}}};rs.directiveName="unsafeHTML",rs.resultType=1,xt(rs);var ns=class extends rs{};ns.directiveName="unsafeSVG",ns.resultType=2;var as=xt(ns),ls=new DOMParser,cs=class extends $e{constructor(){super(...arguments),this.svg="",this.label="",this.library="default"}connectedCallback(){super.connectedCallback(),ts.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,ts=ts.filter((e=>e!==t))}getUrl(){const t=es(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){var t;const e=es(this.library),s=this.getUrl();if(s)try{const o=await async function(t){if(os.has(t))return os.get(t);const e=await function(t,e="cors"){if(ss.has(t))return ss.get(t);const s=fetch(t,{mode:e}).then((async t=>({ok:t.ok,status:t.status,html:await t.text()})));return ss.set(t,s),s}(t),s={ok:e.ok,status:e.status,svg:null};if(e.ok){const t=document.createElement("div");t.innerHTML=e.html;const o=t.firstElementChild;s.svg="svg"===(null==o?void 0:o.tagName.toLowerCase())?o.outerHTML:""}return os.set(t,s),s}(s);if(s!==this.getUrl())return;if(o.ok){const s=ls.parseFromString(o.svg,"text/html").body.querySelector("svg");null!==s?(null==(t=null==e?void 0:e.mutator)||t.call(e,s),this.svg=s.outerHTML,Ee(this,"sl-load")):(this.svg="",Ee(this,"sl-error"))}else this.svg="",Ee(this,"sl-error")}catch(t){Ee(this,"sl-error")}else this.svg.length>0&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return oe` <div
      part="base"
      class="icon"
      role=${qe(t?"img":void 0)}
      aria-label=${qe(t?this.label:void 0)}
      aria-hidden=${qe(t?void 0:"true")}
    >
      ${as(this.svg)}
    </div>`}};cs.styles=is,pt([Me()],cs.prototype,"svg",2),pt([Pe({reflect:!0})],cs.prototype,"name",2),pt([Pe()],cs.prototype,"src",2),pt([Pe()],cs.prototype,"label",2),pt([Pe({reflect:!0})],cs.prototype,"library",2),pt([Se("name"),Se("src"),Se("library")],cs.prototype,"setIcon",1),cs=pt([Te("sl-icon")],cs);const ds=t=>(...e)=>({_$litDirective$:t,values:e});class hs{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const{H:us}=J,ps=(t,e)=>{var s,o;return void 0===e?void 0!==(null===(s=t)||void 0===s?void 0:s._$litType$):(null===(o=t)||void 0===o?void 0:o._$litType$)===e},bs=()=>document.createComment(""),vs=(t,e,s)=>{var o;const i=t._$AA.parentNode,r=void 0===e?t._$AB:e._$AA;if(void 0===s){const e=i.insertBefore(bs(),r),o=i.insertBefore(bs(),r);s=new us(e,o,t,t.options)}else{const e=s._$AB.nextSibling,n=s._$AM,a=n!==t;if(a){let e;null===(o=s._$AQ)||void 0===o||o.call(s,t),s._$AM=t,void 0!==s._$AP&&(e=t._$AU)!==n._$AU&&s._$AP(e)}if(e!==r||a){let t=s._$AA;for(;t!==e;){const e=t.nextSibling;i.insertBefore(t,r),t=e}}}return s},fs={},gs=(t,e=fs)=>t._$AH=e,ms=t=>t._$AH,ys=(t,e)=>{var s,o;const i=t._$AN;if(void 0===i)return!1;for(const t of i)null===(o=(s=t)._$AO)||void 0===o||o.call(s,e,!1),ys(t,e);return!0},_s=t=>{let e,s;do{if(void 0===(e=t._$AM))break;s=e._$AN,s.delete(t),t=e}while(0===(null==s?void 0:s.size))},$s=t=>{for(let e;e=t._$AM;t=e){let s=e._$AN;if(void 0===s)e._$AN=s=new Set;else if(s.has(t))break;s.add(t),xs(e)}};function ws(t){void 0!==this._$AN?(_s(this),this._$AM=t,$s(this)):this._$AM=t}function As(t,e=!1,s=0){const o=this._$AH,i=this._$AN;if(void 0!==i&&0!==i.size)if(e)if(Array.isArray(o))for(let t=s;t<o.length;t++)ys(o[t],!1),_s(o[t]);else null!=o&&(ys(o,!1),_s(o));else ys(this,t)}const xs=t=>{var e,s,o,i;2==t.type&&(null!==(e=(o=t)._$AP)&&void 0!==e||(o._$AP=As),null!==(s=(i=t)._$AQ)&&void 0!==s||(i._$AQ=ws))};class Cs extends hs{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,s){super._$AT(t,e,s),$s(this),this.isConnected=t._$AU}_$AO(t,e=!0){var s,o;t!==this.isConnected&&(this.isConnected=t,t?null===(s=this.reconnected)||void 0===s||s.call(this):null===(o=this.disconnected)||void 0===o||o.call(this)),e&&(ys(this,t),_s(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Ss{constructor(t){this.U=t}disconnect(){this.U=void 0}reconnect(t){this.U=t}deref(){return this.U}}class Es{constructor(){this.Y=void 0,this.q=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Y=this.q=void 0}}const ks=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,Ts=ds(class extends Cs{constructor(){super(...arguments),this._$Cwt=1073741823,this._$Cyt=[],this._$CG=new Ss(this),this._$CK=new Es}render(...t){var e;return null!==(e=t.find((t=>!ks(t))))&&void 0!==e?e:z}update(t,e){const s=this._$Cyt;let o=s.length;this._$Cyt=e;const i=this._$CG,r=this._$CK;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cwt);t++){const n=e[t];if(!ks(n))return this._$Cwt=t,n;t<o&&n===s[t]||(this._$Cwt=1073741823,o=0,Promise.resolve(n).then((async t=>{for(;r.get();)await r.get();const e=i.deref();if(void 0!==e){const s=e._$Cyt.indexOf(n);s>-1&&s<e._$Cwt&&(e._$Cwt=s,e.setValue(t))}})))}return z}disconnected(){this._$CG.disconnect(),this._$CK.pause()}reconnected(){this._$CG.reconnect(this),this._$CK.resume()}});class Us{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class Ps extends et{static properties={src:{type:String},template:{attribute:!1}};static styles=r`
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
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),s=(await fetch(t)).body.getReader();let{value:o,done:i}=await s.read();o=o?e.decode(o,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(o);if(t)yield o.substring(n,t.index),n=r.lastIndex;else{if(i)break;const t=o.substr(n);({value:o,done:i}=await s.read()),o=t+(o?e.decode(o,{stream:!0}):""),n=r.lastIndex=0}}n<o.length&&(yield o.substr(n))}render(){if(!this.src)return H``;const t=this.parseSrc();return H`${Ts(t,H``)}`}}customElements.define("report-table",Ps),customElements.define("sc-intro-tbl",class extends Ps{parseHeader(t){const e=t.split(";");return H`
            <tr>
                ${e.map((t=>H`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=H``,s=!0;for(const o of t.split(";")){const[t,i,r]=o.split("|");let n=H`${t}`;r&&(n=H`<a href=${r}>${n}</a>`),i&&(n=H`<abbr title=${i}>${n}</abbr>`),s?(e=H`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,s=!1):e=H`${e}
                    <td>
                        ${n}
                    </td>
                `}return H`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.src);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Us("first line in intro table file should be a header.");e=e.slice(2);let s=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Us("lines following the first should all be normal table rows.");e=e.slice(2),s=H`${s}${this.parseRow(e)}`}return H`<table>${s}</table>`}});var Ms=Pt`
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
`;function Ns(t,e,s="vertical",o="smooth"){const i=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=i.top+e.scrollTop,n=i.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,c=e.scrollTop,d=e.scrollTop+e.offsetHeight;"horizontal"!==s&&"both"!==s||(n<a?e.scrollTo({left:n,behavior:o}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:o})),"vertical"!==s&&"both"!==s||(r<c?e.scrollTo({top:r,behavior:o}):r+t.clientHeight>d&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:o}))}var Hs,zs=new Set,Os=new MutationObserver(Rs),Ls=new Map,Bs=document.documentElement.lang||navigator.language;function Rs(){Bs=document.documentElement.lang||navigator.language,[...zs.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}Os.observe(document.documentElement,{attributes:!0,attributeFilter:["lang"]});var Ds=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){zs.add(this.host)}hostDisconnected(){zs.delete(this.host)}term(t,...e){return function(t,e,...s){const o=t.toLowerCase().slice(0,2),i=t.length>2?t.toLowerCase():"",r=Ls.get(i),n=Ls.get(o);let a;if(r&&r[e])a=r[e];else if(n&&n[e])a=n[e];else{if(!Hs||!Hs[e])return console.error(`No translation found for: ${e}`),e;a=Hs[e]}return"function"==typeof a?a(...s):a}(this.host.lang||Bs,t,...e)}date(t,e){return function(t,e,s){return e=new Date(e),new Intl.DateTimeFormat(t,s).format(e)}(this.host.lang||Bs,t,e)}number(t,e){return function(t,e,s){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(t,s).format(e)}(this.host.lang||Bs,t,e)}relativeTime(t,e,s){return function(t,e,s,o){return new Intl.RelativeTimeFormat(t,o).format(e,s)}(this.host.lang||Bs,t,e,s)}};!function(...t){t.map((t=>{const e=t.$code.toLowerCase();Ls.set(e,t),Hs||(Hs=t)})),Rs()}({$code:"en",$name:"English",$dir:"ltr",clearEntry:"Clear entry",close:"Close",copy:"Copy",currentValue:"Current value",hidePassword:"Hide password",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",toggleColorFormat:"Toggle color format"});var Is=class extends $e{constructor(){super(...arguments),this.localize=new Ds(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{var s;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(s=this.getActiveTab())?s:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t=!1){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement;if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&"ArrowLeft"===t.key||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s--:(["top","bottom"].includes(this.placement)&&"ArrowRight"===t.key||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&s++,s<0&&(s=this.tabs.length-1),s>this.tabs.length-1&&(s=0),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Ns(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth}setActiveTab(t,e){if(e=ht({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const s=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)})),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Ns(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(s&&Ee(this,"sl-tab-hide",{detail:{name:s.panel}}),Ee(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,s=t.clientHeight,o=this.getAllTabs(!0),i=o.slice(0,o.indexOf(t)).reduce(((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight})),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=`translateX(${i.left}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${s}px`,this.indicator.style.transform=`translateY(${i.top}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.panels=this.getAllPanels(),this.syncIndicator()}render(){return oe`
      <div
        part="base"
        class=${Ae({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?oe`
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

          ${this.hasScrollControls?oe`
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
    `}};Is.styles=Ms,pt([He(".tab-group")],Is.prototype,"tabGroup",2),pt([He(".tab-group__body")],Is.prototype,"body",2),pt([He(".tab-group__nav")],Is.prototype,"nav",2),pt([He(".tab-group__indicator")],Is.prototype,"indicator",2),pt([Me()],Is.prototype,"hasScrollControls",2),pt([Pe()],Is.prototype,"placement",2),pt([Pe()],Is.prototype,"activation",2),pt([Pe({attribute:"no-scroll-controls",type:Boolean})],Is.prototype,"noScrollControls",2),pt([Pe()],Is.prototype,"lang",2),pt([Se("noScrollControls",{waitUntilFirstUpdate:!0})],Is.prototype,"updateScrollControls",1),pt([Se("placement",{waitUntilFirstUpdate:!0})],Is.prototype,"syncIndicator",1),Is=pt([Te("sl-tab-group")],Is);var Fs=0;function js(){return++Fs}var Ws=Pt`
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

  .tab${Be}:not(.tab--disabled) {
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
`,Vs=class extends $e{constructor(){super(...arguments),this.localize=new Ds(this),this.attrId=js(),this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Ee(this,"sl-close")}render(){return this.id=this.id.length>0?this.id:this.componentId,oe`
      <div
        part="base"
        class=${Ae({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        role="tab"
        aria-disabled=${this.disabled?"true":"false"}
        aria-selected=${this.active?"true":"false"}
        tabindex=${this.disabled||!this.active?"-1":"0"}
      >
        <slot></slot>
        ${this.closable?oe`
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
    `}};Vs.styles=Ws,pt([He(".tab")],Vs.prototype,"tab",2),pt([Pe({reflect:!0})],Vs.prototype,"panel",2),pt([Pe({type:Boolean,reflect:!0})],Vs.prototype,"active",2),pt([Pe({type:Boolean})],Vs.prototype,"closable",2),pt([Pe({type:Boolean,reflect:!0})],Vs.prototype,"disabled",2),pt([Pe()],Vs.prototype,"lang",2),Vs=pt([Te("sl-tab")],Vs);var qs=Pt`
  ${xe}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }
`,Ks=class extends $e{constructor(){super(...arguments),this.attrId=js(),this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId}render(){return this.style.display=this.active?"block":"none",oe`
      <div part="base" class="tab-panel" role="tabpanel" aria-hidden=${this.active?"false":"true"}>
        <slot></slot>
      </div>
    `}};Ks.styles=qs,pt([Pe({reflect:!0})],Ks.prototype,"name",2),pt([Pe({type:Boolean,reflect:!0})],Ks.prototype,"active",2),Ks=pt([Te("sl-tab-panel")],Ks);const Gs=ds(class extends hs{constructor(t){super(t),this.tt=new WeakMap}render(t){return[t]}update(t,[e]){if(ps(this.it)&&(!ps(e)||this.it.strings!==e.strings)){const e=ms(t).pop();let s=this.tt.get(this.it.strings);if(void 0===s){const t=document.createDocumentFragment();s=B(O,t),s.setConnected(!1),this.tt.set(this.it.strings,s)}gs(s,[e]),vs(s,void 0,e)}if(ps(e)){if(!ps(this.it)||this.it.strings!==e.strings){const s=this.tt.get(e.strings);if(void 0!==s){const e=ms(s).pop();(t=>{t._$AR()})(t),vs(t,void 0,e),gs(t,[e])}}this.it=e}else this.it=void 0;return this.render(e)}});class Ys extends et{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(t,e){for(const e of t)"active"===e.attributeName&&(this.tabname===e.target.id?this.visible=!0:this.visible=!1)}connectedCallback(){super.connectedCallback();const t=this.checkVisible.bind(this);this.observer=new MutationObserver(t),this.observer.observe(this.parentElement,{attributes:!0})}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return H`
        ${Gs(this.visible?H`${this.visibleTemplate()}`:H``)}`}}customElements.define("wult-tab",Ys);var Zs=Pt`
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
`,Js=class extends $e{render(){return oe`
      <svg part="base" class="spinner" role="status">
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};Js.styles=Zs,Js=pt([Te("sl-spinner")],Js);class Xs extends et{static styles=r`
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
  `;static properties={path:{type:String},_visible:{type:Boolean,state:!0}};connectedCallback(){super.connectedCallback(),this.observer=new IntersectionObserver(((t,e)=>{t.forEach((t=>{t.isIntersecting?this._visible=!0:this._visible=!1}))})),this.observer.observe(this.parentElement)}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}constructor(){super(),this._visible=!1}hideLoading(){this.renderRoot.querySelector("#loading").style.display="none"}render(){return this._visible?H`
                <div id="loading" class="loading">
                    <sl-spinner></sl-spinner>
                </div>
                <div class="plot">
                    <iframe @load=${this.hideLoading} seamless frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
                </div>
            `:H``}}customElements.define("sc-diagram",Xs);var Qs=Pt`
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

  .button${Be} {
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

  .button--text${Be}:not(.button--disabled) {
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
`,to=class extends Event{constructor(t){super("formdata"),this.formData=t}},eo=class extends FormData{constructor(t){var e=(...t)=>{super(...t)};t?(e(t),this.form=t,t.dispatchEvent(new to(this))):e()}append(t,e){if(!this.form)return super.append(t,e);let s=this.form.elements[t];if(s||(s=document.createElement("input"),s.type="hidden",s.name=t,this.form.appendChild(s)),this.has(t)){const o=this.getAll(t),i=o.indexOf(s.value);-1!==i&&o.splice(i,1),o.push(e),this.set(t,o)}else super.append(t,e);s.value=e}};function so(){window.FormData&&!function(){const t=document.createElement("form");let e=!1;return document.body.append(t),t.addEventListener("submit",(t=>{new FormData(t.target),t.preventDefault()})),t.addEventListener("formdata",(()=>e=!0)),t.dispatchEvent(new Event("submit",{cancelable:!0})),t.remove(),e}()&&(window.FormData=eo,window.addEventListener("submit",(t=>{t.defaultPrevented||new FormData(t.target)})))}"complete"===document.readyState?so():window.addEventListener("DOMContentLoaded",(()=>so()));var oo=class extends $e{constructor(){super(...arguments),this.formSubmitController=new class{constructor(t,e){(this.host=t).addController(this),this.options=ht({form:t=>t.closest("form"),name:t=>t.name,value:t=>t.value,disabled:t=>t.disabled,reportValidity:t=>"function"!=typeof t.reportValidity||t.reportValidity()},e),this.handleFormData=this.handleFormData.bind(this),this.handleFormSubmit=this.handleFormSubmit.bind(this)}hostConnected(){this.form=this.options.form(this.host),this.form&&(this.form.addEventListener("formdata",this.handleFormData),this.form.addEventListener("submit",this.handleFormSubmit))}hostDisconnected(){this.form&&(this.form.removeEventListener("formdata",this.handleFormData),this.form.removeEventListener("submit",this.handleFormSubmit),this.form=void 0)}handleFormData(t){const e=this.options.disabled(this.host),s=this.options.name(this.host),o=this.options.value(this.host);e||"string"!=typeof s||void 0===o||(Array.isArray(o)?o.forEach((e=>{t.formData.append(s,e.toString())})):t.formData.append(s,o.toString()))}handleFormSubmit(t){const e=this.options.disabled(this.host),s=this.options.reportValidity;!this.form||this.form.noValidate||e||s(this.host)||(t.preventDefault(),t.stopImmediatePropagation())}submit(t){if(this.form){const e=document.createElement("button");e.type="submit",e.style.position="absolute",e.style.width="0",e.style.height="0",e.style.clipPath="inset(50%)",e.style.overflow="hidden",e.style.whiteSpace="nowrap",t&&["formaction","formmethod","formnovalidate","formtarget"].forEach((s=>{t.hasAttribute(s)&&e.setAttribute(s,t.getAttribute(s))})),this.form.append(e),e.click(),e.remove()}}}(this,{form:t=>{if(t.hasAttribute("form")){const e=t.getRootNode(),s=t.getAttribute("form");return e.getElementById(s)}return t.closest("form")}}),this.hasSlotController=new At(this,"[default]","prefix","suffix"),this.hasFocus=!1,this.variant="default",this.size="medium",this.caret=!1,this.disabled=!1,this.loading=!1,this.outline=!1,this.pill=!1,this.circle=!1,this.type="button"}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Ee(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Ee(this,"sl-focus")}handleClick(t){if(this.disabled||this.loading)return t.preventDefault(),void t.stopPropagation();"submit"===this.type&&this.formSubmitController.submit(this)}render(){const t=!!this.href,e=t?Fe`a`:Fe`button`;return Ve`
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
    `}};oo.styles=Qs,pt([He(".button")],oo.prototype,"button",2),pt([Me()],oo.prototype,"hasFocus",2),pt([Pe({reflect:!0})],oo.prototype,"variant",2),pt([Pe({reflect:!0})],oo.prototype,"size",2),pt([Pe({type:Boolean,reflect:!0})],oo.prototype,"caret",2),pt([Pe({type:Boolean,reflect:!0})],oo.prototype,"disabled",2),pt([Pe({type:Boolean,reflect:!0})],oo.prototype,"loading",2),pt([Pe({type:Boolean,reflect:!0})],oo.prototype,"outline",2),pt([Pe({type:Boolean,reflect:!0})],oo.prototype,"pill",2),pt([Pe({type:Boolean,reflect:!0})],oo.prototype,"circle",2),pt([Pe()],oo.prototype,"type",2),pt([Pe()],oo.prototype,"name",2),pt([Pe()],oo.prototype,"value",2),pt([Pe()],oo.prototype,"href",2),pt([Pe()],oo.prototype,"target",2),pt([Pe()],oo.prototype,"download",2),pt([Pe()],oo.prototype,"form",2),pt([Pe({attribute:"formaction"})],oo.prototype,"formAction",2),pt([Pe({attribute:"formmethod"})],oo.prototype,"formMethod",2),pt([Pe({attribute:"formnovalidate",type:Boolean})],oo.prototype,"formNoValidate",2),pt([Pe({attribute:"formtarget"})],oo.prototype,"formTarget",2),oo=pt([Te("sl-button")],oo);var io=Pt`
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

  .details__header${Be} {
    outline: var(--sl-focus-ring);
    outline-offset: calc(1px + var(--sl-focus-ring-offset));
  }

  .details--disabled .details__header {
    cursor: not-allowed;
  }

  .details--disabled .details__header${Be} {
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
`,ro=class extends $e{constructor(){super(...arguments),this.open=!1,this.disabled=!1}firstUpdated(){this.body.hidden=!this.open,this.body.style.height=this.open?"auto":"0"}async show(){if(!this.open&&!this.disabled)return this.open=!0,ke(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,ke(this,"sl-after-hide")}handleSummaryClick(){this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){Ee(this,"sl-show"),await vt(this.body),this.body.hidden=!1;const{keyframes:t,options:e}=_t(this,"details.show");await bt(this.body,ft(t,this.body.scrollHeight),e),this.body.style.height="auto",Ee(this,"sl-after-show")}else{Ee(this,"sl-hide"),await vt(this.body);const{keyframes:t,options:e}=_t(this,"details.hide");await bt(this.body,ft(t,this.body.scrollHeight),e),this.body.hidden=!0,this.body.style.height="auto",Ee(this,"sl-after-hide")}}render(){return oe`
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
    `}};ro.styles=io,pt([He(".details")],ro.prototype,"details",2),pt([He(".details__header")],ro.prototype,"header",2),pt([He(".details__body")],ro.prototype,"body",2),pt([Pe({type:Boolean,reflect:!0})],ro.prototype,"open",2),pt([Pe()],ro.prototype,"summary",2),pt([Pe({type:Boolean,reflect:!0})],ro.prototype,"disabled",2),pt([Se("open",{waitUntilFirstUpdate:!0})],ro.prototype,"handleOpenChange",1),ro=pt([Te("sl-details")],ro),yt("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),yt("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}});class no extends et{static styles=r`
        .text-field-container {
            overflow: auto;
            max-height: 33vh;
            display: flex;
            flex-direction: column;
        }

        .diff-table {
            width: 100%;
            height: 100%;
            border: none;
        }

        .diff-div {
            height: 33vh;
            display: flex;
            flex-direction: column;
        }

        sl-details::part(base) {
            font-family: Arial, sans-serif;
        }
        sl-details::part(header) {
            font-weight: "bold";
        }
    `;static properties={title:{type:String},paths:{type:Object},diff:{type:String}};getFileContents(t){return new Promise((function(e,s){fetch(t).then((t=>{if(!t.ok)throw new Error(`HTTP error: status ${t.status}`);return t.blob()})).then((t=>t.text())).then((t=>{e(t)}))}))}getNewTabBtnTemplate(t){return H`
            <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${t} target="_blank">
                Open in New Tab
            </sl-button>
        `}getDiffTemplate(){if(this.diff){const t=`${this.title}-diff`;return H`
                <sl-tab class="tab" slot="nav" panel=${t}>Diff</sl-tab>
                <sl-tab-panel class="tab-panel" name=${t}>
                    <div class="diff-div" id=${t}>
                        <div>
                            ${this.getNewTabBtnTemplate(this.diff)}
                        </div>
                        <!-- Diffs are created in the form of an HTML table so
                        viewed using an iframe  -->
                        <iframe seamless class="diff-table" src="${this.diff}"></iframe>
                    </div>
                </sl-tab-panel>
            `}return H``}getTabTemplate(t,e){const s=`details-panel-${this.title}-${t}`;return H`
            <sl-tab class="tab" slot="nav" panel=${s}>${t}</sl-tab>
            <sl-tab-panel class="tab-panel" name=${s}>
                <div class="text-field-container">
                    <div>
                        ${this.getNewTabBtnTemplate(e)}
                    </div>
                    <pre><code>${Ts(this.getFileContents(e),H`Loading...`)}</code></pre>
                </div>
            </sl-tab-panel>
        `}render(){return H`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.paths).map((t=>this.getTabTemplate(t[0],t[1])))}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `}}customElements.define("sc-file-preview",no);class ao{}const lo=new WeakMap,co=ds(class extends Cs{render(t){return O}update(t,[e]){var s;const o=e!==this.U;return o&&void 0!==this.U&&this.ot(void 0),(o||this.rt!==this.lt)&&(this.U=e,this.ht=null===(s=t.options)||void 0===s?void 0:s.host,this.ot(this.lt=t.element)),O}ot(t){var e;if("function"==typeof this.U){const s=null!==(e=this.ht)&&void 0!==e?e:globalThis;let o=lo.get(s);void 0===o&&(o=new WeakMap,lo.set(s,o)),void 0!==o.get(this.U)&&this.U.call(this.ht,void 0),o.set(this.U,t),void 0!==t&&this.U.call(this.ht,t)}else this.U.value=t}get rt(){var t,e,s;return"function"==typeof this.U?null===(e=lo.get(null!==(t=this.ht)&&void 0!==t?t:globalThis))||void 0===e?void 0:e.get(this.U):null===(s=this.U)||void 0===s?void 0:s.value}disconnected(){this.rt===this.lt&&this.ot(void 0)}reconnected(){this.ot(this.lt)}});class ho extends Ps{static styles=[Ps.styles,r`
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
        `];tableRef=(()=>new ao)();removeDetailsEl(t){for(const e of t.childNodes)if("TR"===e.tagName)for(const t of e.childNodes)for(const e of t.childNodes)"SL-DETAILS"===e.tagName&&t.removeChild(e);return t}copyTable(){const t=window.getSelection();t.removeAllRanges();const e=document.createRange();e.selectNodeContents(this.tableRef.value),t.addRange(e),this.removeDetailsEl(t.anchorNode),document.execCommand("copy"),t.removeAllRanges(),this.requestUpdate()}parseMetric(t){const e=t[0].split("|");return H`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,s]=t.split("|");return H`
            <td class="td-value">
                ${s?H`<abbr title=${s}>${e}</abbr>`:H`${e}`}
            </td>
        `}async parseSrc(){let t,e=H``;for await(const s of this.makeTextFileLineIterator(this.src)){const o=s.split(";"),i=o[0];if(o.shift(),"H"===i)for(const t of o)e=H`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===i)t=this.parseMetric(o);else{const s=H`${o.map((t=>this.parseSummaryFunc(t)))}`;e=H`
                    ${e}
                    <tr>
                      ${t}
                      ${s}
                    </tr>
                `,t&&(t=void 0)}}return e=H`<table ${co(this.tableRef)} width=${this.getWidth(this.cols)}>${e}</table>`,H`
            <div style="display:flex;">
                ${e}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}}customElements.define("smry-tbl",ho);class uo extends Ys{static styles=r`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},fpreviews:{type:Array},smrytblpath:{type:String}};visibleTemplate(){return H`
            <br>
            ${this.smrytblpath?H`<smry-tbl .src="${this.smrytblpath}"></smry-tbl>`:H``}
            ${this.fpreviews?this.fpreviews.map((t=>H`
                    <sc-file-preview .title=${t.title} .diff=${t.diff} .paths=${t.paths}></sc-file-preview>
                    <br>
                `)):H``}
            <div class="grid">
                ${this.paths?this.paths.map((t=>H`
                    <sc-diagram path="${t}"></sc-diagram>
                    `)):H``}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",uo);class po extends et{static styles=r`
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
    `;static properties={tabFile:{type:String},tabs:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};updated(t){t.has("tabFile")&&fetch(this.tabFile).then((t=>t.json())).then((t=>{this.tabs=t}))}tabTemplate(t){return t.tabs?H`
                <sl-tab-group>
                    ${t.tabs.map((t=>H`
                        <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                        <sl-tab-panel class="tab-panel" id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                    `))}
                </sl-tab-group>
        `:H`
            <wult-metric-tab tabname=${t.name} .smrytblpath=${t.smrytblpath} .paths=${t.ppaths} .fpreviews=${t.fpreviews} .dir=${t.dir}></wult-metric-tab>
        `}render(){return this.tabs?H`
            <sl-tab-group>
                ${this.tabs.map((t=>H`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
      `:H``}}customElements.define("tab-group",po);class bo extends et{static properties={src:{type:String},reportInfo:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};static styles=r`
        .report-head {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .report-title {
            font-family: Arial, sans-serif;
        }
    `;async connectedCallback(){super.connectedCallback();try{const t=await fetch(this.src);this.reportInfo=await t.json(),this.toolname=this.reportInfo.toolname,this.titleDescr=this.reportInfo.title_descr,this.tabFile=this.reportInfo.tab_file,this.introtbl=this.reportInfo.intro_tbl}catch(t){t instanceof TypeError&&(this.fetchFailed=!0)}}corsWarning(){return H`
        <sl-alert variant="danger" open>
          Warning: it looks like you might be trying to view this report
          locally.  See our documentation on how to do that <a
          href="https://intel.github.io/wult/pages/howto.html#open-wult-reports-locally">
            here.</a>
          </sl-alert>
      `}render(){return this.fetchFailed?this.corsWarning():H`
            <div class="report-head">
                <h1 class="report-title">${this.toolname} report</h1>
                ${this.titleDescr?H`
                    <p class="title_descr">${this.titleDescr}</p>
                    <br>
                    `:H``}

                <sc-intro-tbl .src=${this.introtbl}></sc-intro-tbl>
            </div>
            <br>
            <tab-group .tabFile="${this.tabFile}"></tab-group>
        `}}customElements.define("sc-report-page",bo),Ye("shoelace")})();