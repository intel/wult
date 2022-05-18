/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),s=new Map;class i{constructor(t,s){if(this._$cssResult$=!0,s!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=s.get(this.cssText);return t&&void 0===e&&(s.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const r=t=>new i("string"==typeof t?t:t+"",e),o=(t,...s)=>{const r=1===t.length?t[0]:s.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new i(r,e)},n=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return r(e)})(t):t;var a;const l=window.trustedTypes,h=l?l.emptyScript:"",c=window.reactiveElementPolyfillSupport,d={toAttribute(t,e){switch(e){case Boolean:t=t?h:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},p=(t,e)=>e!==t&&(e==e||t==t),u={attribute:!0,type:String,converter:d,reflect:!1,hasChanged:p};class v extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=u){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const r=this[t];this[e]=i,this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||u}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const s=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{t?e.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const s=document.createElement("style"),i=window.litNonce;void 0!==i&&s.setAttribute("nonce",i),s.textContent=t.cssText,e.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=u){var i,r;const o=this.constructor._$Eh(t,s);if(void 0!==o&&!0===s.reflect){const n=(null!==(r=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==r?r:d.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$Ei=null}}_$AK(t,e){var s,i,r;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==r?r:d.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var b;v.finalized=!0,v.elementProperties=new Map,v.elementStyles=[],v.shadowRootOptions={mode:"open"},null==c||c({ReactiveElement:v}),(null!==(a=globalThis.reactiveElementVersions)&&void 0!==a?a:globalThis.reactiveElementVersions=[]).push("1.2.1");const g=globalThis.trustedTypes,f=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,m=`lit$${(Math.random()+"").slice(9)}$`,$="?"+m,_=`<${$}>`,y=document,w=(t="")=>y.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,E=Array.isArray,x=t=>{var e;return E(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,C=/-->/g,k=/>/g,T=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,U=/'/g,P=/"/g,M=/^(?:script|style|textarea)$/i,O=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),z=O(1),H=(O(2),Symbol.for("lit-noChange")),N=Symbol.for("lit-nothing"),L=new WeakMap,R=(t,e,s)=>{var i,r;const o=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=o._$litPart$;if(void 0===n){const t=null!==(r=null==s?void 0:s.renderBefore)&&void 0!==r?r:null;o._$litPart$=n=new W(e.insertBefore(w(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n},B=y.createTreeWalker(y,129,null,!1),I=(t,e)=>{const s=t.length-1,i=[];let r,o=2===e?"<svg>":"",n=S;for(let e=0;e<s;e++){const s=t[e];let a,l,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,l=n.exec(s),null!==l);)c=n.lastIndex,n===S?"!--"===l[1]?n=C:void 0!==l[1]?n=k:void 0!==l[2]?(M.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=T):void 0!==l[3]&&(n=T):n===T?">"===l[0]?(n=null!=r?r:S,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?T:'"'===l[3]?P:U):n===P||n===U?n=T:n===C||n===k?n=S:(n=T,r=void 0);const d=n===T&&t[e+1].startsWith("/>")?" ":"";o+=n===S?s+_:h>=0?(i.push(a),s.slice(0,h)+"$lit$"+s.slice(h)+m+d):s+m+(-2===h?(i.push(void 0),e):d)}const a=o+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==f?f.createHTML(a):a,i]};class j{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,o=0;const n=t.length-1,a=this.parts,[l,h]=I(t,e);if(this.el=j.createElement(l,s),B.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=B.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(m)){const s=h[o++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(m),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?V:"?"===e[1]?G:"@"===e[1]?J:q})}else a.push({type:6,index:r})}for(const e of t)i.removeAttribute(e)}if(M.test(i.tagName)){const t=i.textContent.split(m),e=t.length-1;if(e>0){i.textContent=g?g.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],w()),B.nextNode(),a.push({type:2,index:++r});i.append(t[e],w())}}}else if(8===i.nodeType)if(i.data===$)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=i.data.indexOf(m,t+1));)a.push({type:7,index:r}),t+=m.length-1}r++}}static createElement(t,e){const s=y.createElement("template");return s.innerHTML=t,s}}function D(t,e,s=t,i){var r,o,n,a;if(e===H)return e;let l=void 0!==i?null===(r=s._$Cl)||void 0===r?void 0:r[i]:s._$Cu;const h=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==h&&(null===(o=null==l?void 0:l._$AO)||void 0===o||o.call(l,!1),void 0===h?l=void 0:(l=new h(t),l._$AT(t,s,i)),void 0!==i?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[i]=l:s._$Cu=l),void 0!==l&&(e=D(t,l._$AS(t,e.values),l,i)),e}class F{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,r=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:y).importNode(s,!0);B.currentNode=r;let o=B.nextNode(),n=0,a=0,l=i[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new W(o,o.nextSibling,this,t):1===l.type?e=new l.ctor(o,l.name,l.strings,this,t):6===l.type&&(e=new Y(o,this,t)),this.v.push(e),l=i[++a]}n!==(null==l?void 0:l.index)&&(o=B.nextNode(),n++)}return r}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class W{constructor(t,e,s,i){var r;this.type=2,this._$AH=N,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(r=null==i?void 0:i.isConnected)||void 0===r||r}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=D(this,t,e),A(t)?t===N||null==t||""===t?(this._$AH!==N&&this._$AR(),this._$AH=N):t!==this._$AH&&t!==H&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):x(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==N&&A(this._$AH)?this._$AA.nextSibling.data=t:this.S(y.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,r="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=j.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===r)this._$AH.m(s);else{const t=new F(r,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=L.get(t.strings);return void 0===e&&L.set(t.strings,e=new j(t)),e}A(t){E(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const r of t)i===e.length?e.push(s=new W(this.M(w()),this.M(w()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class q{constructor(t,e,s,i,r){this.type=1,this._$AH=N,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=N}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const r=this.strings;let o=!1;if(void 0===r)t=D(this,t,e,0),o=!A(t)||t!==this._$AH&&t!==H,o&&(this._$AH=t);else{const i=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=D(this,i[s+n],e,n),a===H&&(a=this._$AH[n]),o||(o=!A(a)||a!==this._$AH[n]),a===N?t=N:t!==N&&(t+=(null!=a?a:"")+r[n+1]),this._$AH[n]=a}o&&!i&&this.k(t)}k(t){t===N?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class V extends q{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===N?void 0:t}}const K=g?g.emptyScript:"";class G extends q{constructor(){super(...arguments),this.type=4}k(t){t&&t!==N?this.element.setAttribute(this.name,K):this.element.removeAttribute(this.name)}}class J extends q{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=D(this,t,e,0))&&void 0!==s?s:N)===H)return;const i=this._$AH,r=t===N&&i!==N||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==N&&(i===N||r);r&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}}class Y{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){D(this,t)}}const Z={P:"$lit$",V:m,L:$,I:1,N:I,R:F,D:x,j:D,H:W,O:q,F:G,B:J,W:V,Z:Y},Q=window.litHtmlPolyfillSupport;var X,tt;null==Q||Q(j,W),(null!==(b=globalThis.litHtmlVersions)&&void 0!==b?b:globalThis.litHtmlVersions=[]).push("2.1.2");class et extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=R(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return H}}et.finalized=!0,et._$litElement$=!0,null===(X=globalThis.litElementHydrateSupport)||void 0===X||X.call(globalThis,{LitElement:et});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:et}),(null!==(tt=globalThis.litElementVersions)&&void 0!==tt?tt:globalThis.litElementVersions=[]).push("3.1.2"),Object.create;var it=Object.defineProperty,rt=Object.defineProperties,ot=Object.getOwnPropertyDescriptor,nt=Object.getOwnPropertyDescriptors,at=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),lt=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),ht=Object.prototype.propertyIsEnumerable,ct=(t,e,s)=>e in t?it(t,e,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[e]=s,dt=(t,e)=>{for(var s in e||(e={}))lt.call(e,s)&&ct(t,s,e[s]);if(at)for(var s of at(e))ht.call(e,s)&&ct(t,s,e[s]);return t},pt=(t,e)=>rt(t,nt(e)),ut=(t,e,s,i)=>{for(var r,o=i>1?void 0:i?ot(e,s):e,n=t.length-1;n>=0;n--)(r=t[n])&&(o=(i?r(e,s,o):r(o))||o);return i&&o&&it(e,s,o),o};function vt(t,e,s){return new Promise((async i=>{if((null==s?void 0:s.duration)===1/0)throw new Error("Promise-based animations must be finite.");const r=t.animate(e,pt(dt({},s),{duration:bt()?0:s.duration}));r.addEventListener("cancel",i,{once:!0}),r.addEventListener("finish",i,{once:!0})}))}function bt(){const t=window.matchMedia("(prefers-reduced-motion: reduce)");return null==t?void 0:t.matches}function gt(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const s=requestAnimationFrame(e);t.addEventListener("cancel",(()=>s),{once:!0}),t.addEventListener("finish",(()=>s),{once:!0}),t.cancel()})))))}var ft=new Map,mt=new WeakMap;function $t(t,e){ft.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function _t(t,e){const s=mt.get(t);if(s&&s[e])return s[e];return ft.get(e)||{keyframes:[],options:{duration:0}}}var yt,wt=t=>(...e)=>({_$litDirective$:t,values:e}),At=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},Et=globalThis.trustedTypes,xt=Et?Et.createPolicy("lit-html",{createHTML:t=>t}):void 0,St=`lit$${(Math.random()+"").slice(9)}$`,Ct="?"+St,kt=`<${Ct}>`,Tt=document,Ut=(t="")=>Tt.createComment(t),Pt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Mt=Array.isArray,Ot=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,zt=/-->/g,Ht=/>/g,Nt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,Lt=/'/g,Rt=/"/g,Bt=/^(?:script|style|textarea)$/i,It=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),jt=It(1),Dt=(It(2),Symbol.for("lit-noChange")),Ft=Symbol.for("lit-nothing"),Wt=new WeakMap,qt=Tt.createTreeWalker(Tt,129,null,!1),Vt=class{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,o=0;const n=t.length-1,a=this.parts,[l,h]=((t,e)=>{const s=t.length-1,i=[];let r,o=2===e?"<svg>":"",n=Ot;for(let e=0;e<s;e++){const s=t[e];let a,l,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,l=n.exec(s),null!==l);)c=n.lastIndex,n===Ot?"!--"===l[1]?n=zt:void 0!==l[1]?n=Ht:void 0!==l[2]?(Bt.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=Nt):void 0!==l[3]&&(n=Nt):n===Nt?">"===l[0]?(n=null!=r?r:Ot,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Nt:'"'===l[3]?Rt:Lt):n===Rt||n===Lt?n=Nt:n===zt||n===Ht?n=Ot:(n=Nt,r=void 0);const d=n===Nt&&t[e+1].startsWith("/>")?" ":"";o+=n===Ot?s+kt:h>=0?(i.push(a),s.slice(0,h)+"$lit$"+s.slice(h)+St+d):s+St+(-2===h?(i.push(void 0),e):d)}const a=o+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==xt?xt.createHTML(a):a,i]})(t,e);if(this.el=Vt.createElement(l,s),qt.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=qt.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(St)){const s=h[o++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(St),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Yt:"?"===e[1]?Qt:"@"===e[1]?Xt:Jt})}else a.push({type:6,index:r})}for(const e of t)i.removeAttribute(e)}if(Bt.test(i.tagName)){const t=i.textContent.split(St),e=t.length-1;if(e>0){i.textContent=Et?Et.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],Ut()),qt.nextNode(),a.push({type:2,index:++r});i.append(t[e],Ut())}}}else if(8===i.nodeType)if(i.data===Ct)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=i.data.indexOf(St,t+1));)a.push({type:7,index:r}),t+=St.length-1}r++}}static createElement(t,e){const s=Tt.createElement("template");return s.innerHTML=t,s}};function Kt(t,e,s=t,i){var r,o,n,a;if(e===Dt)return e;let l=void 0!==i?null===(r=s._$Cl)||void 0===r?void 0:r[i]:s._$Cu;const h=Pt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==h&&(null===(o=null==l?void 0:l._$AO)||void 0===o||o.call(l,!1),void 0===h?l=void 0:(l=new h(t),l._$AT(t,s,i)),void 0!==i?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[i]=l:s._$Cu=l),void 0!==l&&(e=Kt(t,l._$AS(t,e.values),l,i)),e}var Gt=class{constructor(t,e,s,i){var r;this.type=2,this._$AH=Ft,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(r=null==i?void 0:i.isConnected)||void 0===r||r}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Kt(this,t,e),Pt(t)?t===Ft||null==t||""===t?(this._$AH!==Ft&&this._$AR(),this._$AH=Ft):t!==this._$AH&&t!==Dt&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):(t=>{var e;return Mt(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==Ft&&Pt(this._$AH)?this._$AA.nextSibling.data=t:this.S(Tt.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,r="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Vt.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===r)this._$AH.m(s);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,r=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Tt).importNode(s,!0);qt.currentNode=r;let o=qt.nextNode(),n=0,a=0,l=i[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new Gt(o,o.nextSibling,this,t):1===l.type?e=new l.ctor(o,l.name,l.strings,this,t):6===l.type&&(e=new te(o,this,t)),this.v.push(e),l=i[++a]}n!==(null==l?void 0:l.index)&&(o=qt.nextNode(),n++)}return r}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}(r,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=Wt.get(t.strings);return void 0===e&&Wt.set(t.strings,e=new Vt(t)),e}A(t){Mt(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const r of t)i===e.length?e.push(s=new Gt(this.M(Ut()),this.M(Ut()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Jt=class{constructor(t,e,s,i,r){this.type=1,this._$AH=Ft,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=Ft}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const r=this.strings;let o=!1;if(void 0===r)t=Kt(this,t,e,0),o=!Pt(t)||t!==this._$AH&&t!==Dt,o&&(this._$AH=t);else{const i=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=Kt(this,i[s+n],e,n),a===Dt&&(a=this._$AH[n]),o||(o=!Pt(a)||a!==this._$AH[n]),a===Ft?t=Ft:t!==Ft&&(t+=(null!=a?a:"")+r[n+1]),this._$AH[n]=a}o&&!i&&this.k(t)}k(t){t===Ft?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Yt=class extends Jt{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===Ft?void 0:t}},Zt=Et?Et.emptyScript:"",Qt=class extends Jt{constructor(){super(...arguments),this.type=4}k(t){t&&t!==Ft?this.element.setAttribute(this.name,Zt):this.element.removeAttribute(this.name)}},Xt=class extends Jt{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=Kt(this,t,e,0))&&void 0!==s?s:Ft)===Dt)return;const i=this._$AH,r=t===Ft&&i!==Ft||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==Ft&&(i===Ft||r);r&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}},te=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){Kt(this,t)}},ee=window.litHtmlPolyfillSupport;null==ee||ee(Vt,Gt),(null!==(yt=globalThis.litHtmlVersions)&&void 0!==yt?yt:globalThis.litHtmlVersions=[]).push("2.1.0");var se,ie,re,oe=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ne=Symbol(),ae=new Map,le=class{constructor(t,e){if(this._$cssResult$=!0,e!==ne)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=ae.get(this.cssText);return oe&&void 0===t&&(ae.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},he=t=>new le("string"==typeof t?t:t+"",ne),ce=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new le(s,ne)},de=oe?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return he(e)})(t):t,pe=window.trustedTypes,ue=pe?pe.emptyScript:"",ve=window.reactiveElementPolyfillSupport,be={toAttribute(t,e){switch(e){case Boolean:t=t?ue:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},ge=(t,e)=>e!==t&&(e==e||t==t),fe={attribute:!0,type:String,converter:be,reflect:!1,hasChanged:ge},me=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=fe){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const r=this[t];this[e]=i,this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||fe}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(de(t))}else void 0!==t&&e.push(de(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,oe?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=fe){var i,r;const o=this.constructor._$Eh(t,s);if(void 0!==o&&!0===s.reflect){const n=(null!==(r=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==r?r:be.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$Ei=null}}_$AK(t,e){var s,i,r;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==r?r:be.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||ge)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}};me.finalized=!0,me.elementProperties=new Map,me.elementStyles=[],me.shadowRootOptions={mode:"open"},null==ve||ve({ReactiveElement:me}),(null!==(se=globalThis.reactiveElementVersions)&&void 0!==se?se:globalThis.reactiveElementVersions=[]).push("1.1.0");var $e=class extends me{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,s)=>{var i,r;const o=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=o._$litPart$;if(void 0===n){const t=null!==(r=null==s?void 0:s.renderBefore)&&void 0!==r?r:null;o._$litPart$=n=new Gt(e.insertBefore(Ut(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return Dt}};$e.finalized=!0,$e._$litElement$=!0,null===(ie=globalThis.litElementHydrateSupport)||void 0===ie||ie.call(globalThis,{LitElement:$e});var _e=globalThis.litElementPolyfillSupport;null==_e||_e({LitElement:$e}),(null!==(re=globalThis.litElementVersions)&&void 0!==re?re:globalThis.litElementVersions=[]).push("3.1.0");var ye,we=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Ae=Symbol(),Ee=new Map,xe=t=>new class{constructor(t,e){if(this._$cssResult$=!0,e!==Ae)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=Ee.get(this.cssText);return we&&void 0===t&&(Ee.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}}("string"==typeof t?t:t+"",Ae),Se=we?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return xe(e)})(t):t,Ce=window.trustedTypes,ke=Ce?Ce.emptyScript:"",Te=window.reactiveElementPolyfillSupport,Ue={toAttribute(t,e){switch(e){case Boolean:t=t?ke:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},Pe=(t,e)=>e!==t&&(e==e||t==t),Me={attribute:!0,type:String,converter:Ue,reflect:!1,hasChanged:Pe},Oe=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=Me){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const r=this[t];this[e]=i,this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Me}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(Se(t))}else void 0!==t&&e.push(Se(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,we?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=Me){var i,r;const o=this.constructor._$Eh(t,s);if(void 0!==o&&!0===s.reflect){const n=(null!==(r=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==r?r:Ue.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$Ei=null}}_$AK(t,e){var s,i,r;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==r?r:Ue.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||Pe)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}};Oe.finalized=!0,Oe.elementProperties=new Map,Oe.elementStyles=[],Oe.shadowRootOptions={mode:"open"},null==Te||Te({ReactiveElement:Oe}),(null!==(ye=globalThis.reactiveElementVersions)&&void 0!==ye?ye:globalThis.reactiveElementVersions=[]).push("1.1.0");var ze=wt(class extends At{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var s,i;if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.et=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(s=this.et)||void 0===s?void 0:s.has(t))&&this.st.add(t);return this.render(e)}const r=t.element.classList;this.st.forEach((t=>{t in e||(r.remove(t),this.st.delete(t))}));for(const t in e){const s=!!e[t];s===this.st.has(t)||(null===(i=this.et)||void 0===i?void 0:i.has(t))||(s?(r.add(t),this.st.add(t)):(r.remove(t),this.st.delete(t)))}return Dt}}),He=ce`
  .sl-scroll-lock {
    overflow: hidden !important;
  }

  .sl-toast-stack {
    position: fixed;
    top: 0;
    right: 0;
    z-index: var(--sl-z-index-toast);
    width: 28rem;
    max-width: 100%;
    max-height: 100%;
    overflow: auto;
  }

  .sl-toast-stack sl-alert {
    --box-shadow: var(--sl-shadow-large);
    margin: var(--sl-spacing-medium);
  }
`,Ne=ce`
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
`,Le=document.createElement("style");Le.textContent=He.toString(),document.head.append(Le);var Re=ce`
  ${Ne}

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

  .alert__icon {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-large);
  }

  .alert__icon ::slotted(*) {
    margin-left: var(--sl-spacing-large);
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

  .alert__close {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-large);
    padding-right: var(--sl-spacing-medium);
  }
`;function Be(t,e){return(s,i)=>{const{update:r}=s;e=Object.assign({waitUntilFirstUpdate:!1},e),s.update=function(s){if(s.has(t)){const r=s.get(t),o=this[t];r!==o&&((null==e?void 0:e.waitUntilFirstUpdate)&&!this.hasUpdated||this[i].call(this,r,o))}r.call(this,s)}}}function Ie(t,e,s){const i=new CustomEvent(e,Object.assign({bubbles:!0,cancelable:!1,composed:!0,detail:{}},s));return t.dispatchEvent(i),i}function je(t,e){return new Promise((s=>{t.addEventListener(e,(function i(r){r.target===t&&(t.removeEventListener(e,i),s())}))}))}var De=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:s,elements:i}=e;return{kind:s,elements:i,finisher(e){window.customElements.define(t,e)}}})(t,e),Fe=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?pt(dt({},e),{finisher(s){s.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(s){s.createProperty(e.key,t)}};function We(t){return(e,s)=>void 0!==s?((t,e,s)=>{e.constructor.createProperty(s,t)})(t,e,s):Fe(t,e)}function qe(t){return We(pt(dt({},t),{state:!0}))}function Ve(t,e){return(({finisher:t,descriptor:e})=>(s,i)=>{var r;if(void 0===i){const i=null!==(r=s.originalKey)&&void 0!==r?r:s.key,o=null!=e?{kind:"method",placement:"prototype",key:i,descriptor:e(s.key)}:pt(dt({},s),{key:i});return null!=t&&(o.finisher=function(e){t(e,i)}),o}{const r=s.constructor;void 0!==e&&Object.defineProperty(s,i,e(i)),null==t||t(r,i)}})({descriptor:s=>{const i={get(){var e,s;return null!==(s=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==s?s:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof s?Symbol():"__"+s;i.get=function(){var s,i;return void 0===this[e]&&(this[e]=null!==(i=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(t))&&void 0!==i?i:null),this[e]}}return i}})}var Ke=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Ge=class extends $e{constructor(){super(...arguments),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,je(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,je(this,"sl-after-hide")}async toast(){return new Promise((t=>{Ke.parentElement||document.body.append(Ke),Ke.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{Ke.removeChild(this),t(),Ke.querySelector("sl-alert")||Ke.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){Ie(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await gt(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=_t(this,"alert.show");await vt(this.base,t,e),Ie(this,"sl-after-show")}else{Ie(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await gt(this.base);const{keyframes:t,options:e}=_t(this,"alert.hide");await vt(this.base,t,e),this.base.hidden=!0,Ie(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return jt`
      <div
        part="base"
        class=${ze({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
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

        ${this.closable?jt`
              <span class="alert__close">
                <sl-icon-button
                  exportparts="base:close-button"
                  name="x"
                  library="system"
                  @click=${this.handleCloseClick}
                ></sl-icon-button>
              </span>
            `:""}
      </div>
    `}};Ge.styles=Re,ut([Ve('[part="base"]')],Ge.prototype,"base",2),ut([We({type:Boolean,reflect:!0})],Ge.prototype,"open",2),ut([We({type:Boolean,reflect:!0})],Ge.prototype,"closable",2),ut([We({reflect:!0})],Ge.prototype,"variant",2),ut([We({type:Number})],Ge.prototype,"duration",2),ut([Be("open",{waitUntilFirstUpdate:!0})],Ge.prototype,"handleOpenChange",1),ut([Be("duration")],Ge.prototype,"handleDurationChange",1),Ge=ut([De("sl-alert")],Ge),$t("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),$t("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var Je=(()=>{const t=document.createElement("style");let e;try{document.head.appendChild(t),t.sheet.insertRule(":focus-visible { color: inherit }"),e=!0}catch(t){e=!1}finally{t.remove()}return e})(),Ye=he(Je?":focus-visible":":focus"),Ze=ce`
  ${Ne}

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

  .icon-button${Ye} {
    box-shadow: var(--sl-focus-ring);
  }
`,Qe=t=>null!=t?t:Ft,Xe=class extends $e{constructor(){super(...arguments),this.label="",this.disabled=!1}render(){const t=!!this.href,e=jt`
      <sl-icon
        name=${Qe(this.name)}
        library=${Qe(this.library)}
        src=${Qe(this.src)}
        aria-hidden="true"
      ></sl-icon>
    `;return t?jt`
          <a
            part="base"
            class="icon-button"
            href=${Qe(this.href)}
            target=${Qe(this.target)}
            download=${Qe(this.download)}
            rel=${Qe(this.target?"noreferrer noopener":void 0)}
            role="button"
            aria-disabled=${this.disabled?"true":"false"}
            aria-label="${this.label}"
            tabindex=${this.disabled?"-1":"0"}
          >
            ${e}
          </a>
        `:jt`
          <button
            part="base"
            class=${ze({"icon-button":!0,"icon-button--disabled":this.disabled})}
            ?disabled=${this.disabled}
            type="button"
            aria-label=${this.label}
          >
            ${e}
          </button>
        `}};Xe.styles=Ze,ut([Ve("button")],Xe.prototype,"button",2),ut([We()],Xe.prototype,"name",2),ut([We()],Xe.prototype,"library",2),ut([We()],Xe.prototype,"src",2),ut([We()],Xe.prototype,"href",2),ut([We()],Xe.prototype,"target",2),ut([We()],Xe.prototype,"download",2),ut([We()],Xe.prototype,"label",2),ut([We({type:Boolean,reflect:!0})],Xe.prototype,"disabled",2),Xe=ut([De("sl-icon-button")],Xe);var ts="";function es(t){ts=t}var ss=[...document.getElementsByTagName("script")],is=ss.find((t=>t.hasAttribute("data-shoelace")));if(is)es(is.getAttribute("data-shoelace"));else{const t=ss.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let e="";t&&(e=t.getAttribute("src")),es(e.split("/").slice(0,-1).join("/"))}var rs={check:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">\n      <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},os=[{name:"default",resolver:t=>`${ts.replace(/\/$/,"")}/assets/icons/${t}.svg`},{name:"system",resolver:t=>rs[t]?`data:image/svg+xml,${encodeURIComponent(rs[t])}`:""}],ns=[];function as(t){return os.filter((e=>e.name===t))[0]}var ls=new Map,hs=ce`
  ${Ne}

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
`,cs=class extends At{constructor(t){if(super(t),this.it=Ft,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===Ft||null==t)return this.vt=void 0,this.it=t;if(t===Dt)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.vt;this.it=t;const e=[t];return e.raw=e,this.vt={_$litType$:this.constructor.resultType,strings:e,values:[]}}};cs.directiveName="unsafeHTML",cs.resultType=1,wt(cs);var ds=class extends cs{};ds.directiveName="unsafeSVG",ds.resultType=2;var ps=wt(ds),us=new DOMParser,vs=class extends $e{constructor(){super(...arguments),this.svg="",this.library="default"}connectedCallback(){super.connectedCallback(),ns.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,ns=ns.filter((e=>e!==t))}getUrl(){const t=as(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){const t=as(this.library),e=this.getUrl();if(e)try{const s=await(t=>{if(ls.has(t))return ls.get(t);{const e=fetch(t).then((async t=>{if(t.ok){const e=document.createElement("div");e.innerHTML=await t.text();const s=e.firstElementChild;return{ok:t.ok,status:t.status,svg:s&&"svg"===s.tagName.toLowerCase()?s.outerHTML:""}}return{ok:t.ok,status:t.status,svg:null}}));return ls.set(t,e),e}})(e);if(e!==this.getUrl())return;if(s.ok){const e=us.parseFromString(s.svg,"text/html").body.querySelector("svg");e?(t&&t.mutator&&t.mutator(e),this.svg=e.outerHTML,Ie(this,"sl-load")):(this.svg="",Ie(this,"sl-error",{detail:{status:s.status}}))}else this.svg="",Ie(this,"sl-error",{detail:{status:s.status}})}catch(t){Ie(this,"sl-error",{detail:{status:-1}})}else this.svg&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return jt` <div
      part="base"
      class="icon"
      role=${Qe(t?"img":void 0)}
      aria-label=${Qe(t?this.label:void 0)}
      aria-hidden=${Qe(t?void 0:"true")}
    >
      ${ps(this.svg)}
    </div>`}};vs.styles=hs,ut([qe()],vs.prototype,"svg",2),ut([We()],vs.prototype,"name",2),ut([We()],vs.prototype,"src",2),ut([We()],vs.prototype,"label",2),ut([We()],vs.prototype,"library",2),ut([Be("name"),Be("src"),Be("library")],vs.prototype,"setIcon",1),vs=ut([De("sl-icon")],vs);const bs=t=>(...e)=>({_$litDirective$:t,values:e});class gs{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const{H:fs}=Z,ms=(t,e)=>{var s,i;return void 0===e?void 0!==(null===(s=t)||void 0===s?void 0:s._$litType$):(null===(i=t)||void 0===i?void 0:i._$litType$)===e},$s=()=>document.createComment(""),_s=(t,e,s)=>{var i;const r=t._$AA.parentNode,o=void 0===e?t._$AB:e._$AA;if(void 0===s){const e=r.insertBefore($s(),o),i=r.insertBefore($s(),o);s=new fs(e,i,t,t.options)}else{const e=s._$AB.nextSibling,n=s._$AM,a=n!==t;if(a){let e;null===(i=s._$AQ)||void 0===i||i.call(s,t),s._$AM=t,void 0!==s._$AP&&(e=t._$AU)!==n._$AU&&s._$AP(e)}if(e!==o||a){let t=s._$AA;for(;t!==e;){const e=t.nextSibling;r.insertBefore(t,o),t=e}}}return s},ys={},ws=(t,e=ys)=>t._$AH=e,As=t=>t._$AH,Es=(t,e)=>{var s,i;const r=t._$AN;if(void 0===r)return!1;for(const t of r)null===(i=(s=t)._$AO)||void 0===i||i.call(s,e,!1),Es(t,e);return!0},xs=t=>{let e,s;do{if(void 0===(e=t._$AM))break;s=e._$AN,s.delete(t),t=e}while(0===(null==s?void 0:s.size))},Ss=t=>{for(let e;e=t._$AM;t=e){let s=e._$AN;if(void 0===s)e._$AN=s=new Set;else if(s.has(t))break;s.add(t),Ts(e)}};function Cs(t){void 0!==this._$AN?(xs(this),this._$AM=t,Ss(this)):this._$AM=t}function ks(t,e=!1,s=0){const i=this._$AH,r=this._$AN;if(void 0!==r&&0!==r.size)if(e)if(Array.isArray(i))for(let t=s;t<i.length;t++)Es(i[t],!1),xs(i[t]);else null!=i&&(Es(i,!1),xs(i));else Es(this,t)}const Ts=t=>{var e,s,i,r;2==t.type&&(null!==(e=(i=t)._$AP)&&void 0!==e||(i._$AP=ks),null!==(s=(r=t)._$AQ)&&void 0!==s||(r._$AQ=Cs))};class Us extends gs{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,s){super._$AT(t,e,s),Ss(this),this.isConnected=t._$AU}_$AO(t,e=!0){var s,i;t!==this.isConnected&&(this.isConnected=t,t?null===(s=this.reconnected)||void 0===s||s.call(this):null===(i=this.disconnected)||void 0===i||i.call(this)),e&&(Es(this,t),xs(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Ps{constructor(t){this.U=t}disconnect(){this.U=void 0}reconnect(t){this.U=t}deref(){return this.U}}class Ms{constructor(){this.Y=void 0,this.q=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Y=this.q=void 0}}const Os=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,zs=bs(class extends Us{constructor(){super(...arguments),this._$Cft=1073741823,this._$Cwt=[],this._$CG=new Ps(this),this._$CK=new Ms}render(...t){var e;return null!==(e=t.find((t=>!Os(t))))&&void 0!==e?e:H}update(t,e){const s=this._$Cwt;let i=s.length;this._$Cwt=e;const r=this._$CG,o=this._$CK;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cft);t++){const n=e[t];if(!Os(n))return this._$Cft=t,n;t<i&&n===s[t]||(this._$Cft=1073741823,i=0,Promise.resolve(n).then((async t=>{for(;o.get();)await o.get();const e=r.deref();if(void 0!==e){const s=e._$Cwt.indexOf(n);s>-1&&s<e._$Cft&&(e._$Cft=s,e.setValue(t))}})))}return H}disconnected(){this._$CG.disconnect(),this._$CK.pause()}reconnected(){this._$CG.reconnect(this),this._$CK.resume()}});class Hs{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class Ns extends et{static properties={src:{type:String},template:{attribute:!1}};static styles=o`
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
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),s=(await fetch(t)).body.getReader();let{value:i,done:r}=await s.read();i=i?e.decode(i,{stream:!0}):"";const o=/\r\n|\n|\r/gm;let n=0;for(;;){const t=o.exec(i);if(t)yield i.substring(n,t.index),n=o.lastIndex;else{if(r)break;const t=i.substr(n);({value:i,done:r}=await s.read()),i=t+(i?e.decode(i,{stream:!0}):""),n=o.lastIndex=0}}n<i.length&&(yield i.substr(n))}render(){if(!this.src)return z``;const t=this.parseSrc();return z`${zs(t,z``)}`}}customElements.define("report-table",Ns),customElements.define("intro-tbl",class extends Ns{parseHeader(t){const e=t.split(";");return z`
            <tr>
                ${e.map((t=>z`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=z``,s=!0;for(const i of t.split(";")){const[t,r,o]=i.split("|");let n=z`${t}`;o&&(n=z`<a href=${o}>${n}</a>`),r&&(n=z`<abbr title=${r}>${n}</abbr>`),s?(e=z`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,s=!1):e=z`${e}
                    <td>
                        ${n}
                    </td>
                `}return z`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.src);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Hs("first line in intro table file should be a header.");e=e.slice(2);let s=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Hs("lines following the first should all be normal table rows.");e=e.slice(2),s=z`${s}${this.parseRow(e)}`}return z`<table>${s}</table>`}});var Ls,Rs=ce`
  ${Ne}

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
`,Bs=new Set,Is=new MutationObserver(Fs),js=new Map,Ds=document.documentElement.lang||navigator.language;function Fs(){Ds=document.documentElement.lang||navigator.language,[...Bs.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}Is.observe(document.documentElement,{attributes:!0,attributeFilter:["lang"]});var Ws=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Bs.add(this.host)}hostDisconnected(){Bs.delete(this.host)}term(t,...e){return function(t,e,...s){const i=t.toLowerCase().slice(0,2),r=t.length>2?t.toLowerCase():"",o=js.get(r),n=js.get(i);let a;if(o&&o[e])a=o[e];else if(n&&n[e])a=n[e];else{if(!Ls||!Ls[e])return console.error(`No translation found for: ${e}`),e;a=Ls[e]}return"function"==typeof a?a(...s):a}(this.host.lang||Ds,t,...e)}date(t,e){return function(t,e,s){return e=new Date(e),new Intl.DateTimeFormat(t,s).format(e)}(this.host.lang||Ds,t,e)}number(t,e){return function(t,e,s){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(t,s).format(e)}(this.host.lang||Ds,t,e)}relativeTime(t,e,s){return function(t,e,s,i){return new Intl.RelativeTimeFormat(t,i).format(e,s)}(this.host.lang||Ds,t,e,s)}};function qs(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}function Vs(t,e,s="vertical",i="smooth"){const r=qs(t,e),o=r.top+e.scrollTop,n=r.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,h=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==s&&"both"!==s||(n<a?e.scrollTo({left:n,behavior:i}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:i})),"vertical"!==s&&"both"!==s||(o<h?e.scrollTo({top:o,behavior:i}):o+t.clientHeight>c&&e.scrollTo({top:o-e.offsetHeight+t.clientHeight,behavior:i}))}!function(...t){t.map((t=>{const e=t.$code.toLowerCase();js.set(e,t),Ls||(Ls=t)})),Fs()}({$code:"en",$name:"English",$dir:"ltr",close:"Close",copy:"Copy",progress:"Progress",resize:"Resize",scroll_to_end:"Scroll to end",scroll_to_start:"Scroll to start",select_a_color_from_the_screen:"Select a color from the screen",toggle_color_format:"Toggle color format"});var Ks=class extends $e{constructor(){super(...arguments),this.localize=new Ws(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(this.getActiveTab()||this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t=!1){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement;if(e&&"sl-tab"===e.tagName.toLowerCase()){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&"ArrowLeft"===t.key||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s=Math.max(0,s-1):(["top","bottom"].includes(this.placement)&&"ArrowRight"===t.key||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&(s=Math.min(this.tabs.length-1,s+1)),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Vs(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.nav&&(this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth)}setActiveTab(t,e){if(e=Object.assign({emitEvents:!0,scrollBehavior:"auto"},e),t&&t!==this.activeTab&&!t.disabled){const s=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>t.active=t.name===this.activeTab.panel)),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Vs(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(s&&Ie(this,"sl-tab-hide",{detail:{name:s.panel}}),Ie(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.map((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){if(this.indicator){if(!this.getActiveTab())return void(this.indicator.style.display="none");this.indicator.style.display="block",this.repositionIndicator()}}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,s=t.clientHeight,i=qs(t,this.nav),r=i.top+this.nav.scrollTop,o=i.left+this.nav.scrollLeft;switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=`translateX(${o}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${s}px`,this.indicator.style.transform=`translateY(${r}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.panels=this.getAllPanels(),this.syncIndicator()}render(){return jt`
      <div
        part="base"
        class=${ze({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?jt`
                <sl-icon-button
                  class="tab-group__scroll-button tab-group__scroll-button--start"
                  exportparts="base:scroll-button"
                  name="chevron-left"
                  library="system"
                  label=${this.localize.term("scroll_to_start")}
                  @click=${this.handleScrollToStart}
                ></sl-icon-button>
              `:""}

          <div class="tab-group__nav">
            <div part="tabs" class="tab-group__tabs" role="tablist">
              <div part="active-tab-indicator" class="tab-group__indicator"></div>
              <slot name="nav" @slotchange=${this.syncTabsAndPanels}></slot>
            </div>
          </div>

          ${this.hasScrollControls?jt`
                <sl-icon-button
                  class="tab-group__scroll-button tab-group__scroll-button--end"
                  exportparts="base:scroll-button"
                  name="chevron-right"
                  library="system"
                  label=${this.localize.term("scroll_to_end")}
                  @click=${this.handleScrollToEnd}
                ></sl-icon-button>
              `:""}
        </div>

        <div part="body" class="tab-group__body">
          <slot @slotchange=${this.syncTabsAndPanels}></slot>
        </div>
      </div>
    `}};Ks.styles=Rs,ut([Ve(".tab-group")],Ks.prototype,"tabGroup",2),ut([Ve(".tab-group__body")],Ks.prototype,"body",2),ut([Ve(".tab-group__nav")],Ks.prototype,"nav",2),ut([Ve(".tab-group__indicator")],Ks.prototype,"indicator",2),ut([qe()],Ks.prototype,"hasScrollControls",2),ut([We()],Ks.prototype,"placement",2),ut([We()],Ks.prototype,"activation",2),ut([We({attribute:"no-scroll-controls",type:Boolean})],Ks.prototype,"noScrollControls",2),ut([We()],Ks.prototype,"lang",2),ut([Be("noScrollControls")],Ks.prototype,"updateScrollControls",1),ut([Be("placement")],Ks.prototype,"syncIndicator",1),Ks=ut([De("sl-tab-group")],Ks);var Gs=ce`
  ${Ne}

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

  .tab${Ye}:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
    box-shadow: inset var(--sl-focus-ring);
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
`,Js=0,Ys=class extends $e{constructor(){super(...arguments),this.localize=new Ws(this),this.componentId="sl-tab-"+ ++Js,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Ie(this,"sl-close")}render(){return this.id=this.id||this.componentId,jt`
      <div
        part="base"
        class=${ze({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        role="tab"
        aria-disabled=${this.disabled?"true":"false"}
        aria-selected=${this.active?"true":"false"}
        tabindex=${this.disabled||!this.active?"-1":"0"}
      >
        <slot></slot>
        ${this.closable?jt`
              <sl-icon-button
                name="x"
                library="system"
                label=${this.localize.term("close")}
                exportparts="base:close-button"
                class="tab__close-button"
                @click=${this.handleCloseClick}
                tabindex="-1"
              ></sl-icon-button>
            `:""}
      </div>
    `}};Ys.styles=Gs,ut([Ve(".tab")],Ys.prototype,"tab",2),ut([We({reflect:!0})],Ys.prototype,"panel",2),ut([We({type:Boolean,reflect:!0})],Ys.prototype,"active",2),ut([We({type:Boolean})],Ys.prototype,"closable",2),ut([We({type:Boolean,reflect:!0})],Ys.prototype,"disabled",2),ut([We()],Ys.prototype,"lang",2),Ys=ut([De("sl-tab")],Ys);var Zs=ce`
  ${Ne}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }
`,Qs=0,Xs=class extends $e{constructor(){super(...arguments),this.componentId="sl-tab-panel-"+ ++Qs,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id||this.componentId}render(){return this.style.display=this.active?"block":"none",jt`
      <div part="base" class="tab-panel" role="tabpanel" aria-hidden=${this.active?"false":"true"}>
        <slot></slot>
      </div>
    `}};Xs.styles=Zs,ut([We({reflect:!0})],Xs.prototype,"name",2),ut([We({type:Boolean,reflect:!0})],Xs.prototype,"active",2),Xs=ut([De("sl-tab-panel")],Xs);const ti=bs(class extends gs{constructor(t){super(t),this.tt=new WeakMap}render(t){return[t]}update(t,[e]){if(ms(this.it)&&(!ms(e)||this.it.strings!==e.strings)){const e=As(t).pop();let s=this.tt.get(this.it.strings);if(void 0===s){const t=document.createDocumentFragment();s=R(N,t),s.setConnected(!1),this.tt.set(this.it.strings,s)}ws(s,[e]),_s(s,void 0,e)}if(ms(e)){if(!ms(this.it)||this.it.strings!==e.strings){const s=this.tt.get(e.strings);if(void 0!==s){const e=As(s).pop();(t=>{t._$AR()})(t),_s(t,void 0,e),ws(t,[e])}}this.it=e}else this.it=void 0;return this.render(e)}});class ei extends et{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(t,e){for(const e of t)"active"===e.attributeName&&(this.tabname===e.target.id?this.visible=!0:this.visible=!1)}connectedCallback(){super.connectedCallback();const t=this.checkVisible.bind(this);this.observer=new MutationObserver(t),this.observer.observe(this.parentElement,{attributes:!0})}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return z`
        ${ti(this.visible?z`${this.visibleTemplate()}`:z``)}`}}customElements.define("wult-tab",ei);var si=ce`
  ${Ne}

  :host {
    --track-width: 2px;
    --track-color: rgb(128 128 128 / 25%);
    --indicator-color: var(--sl-color-primary-600);
    --speed: 800ms;

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
    }

    100% {
      transform: rotate(360deg);
    }
  }
`,ii=class extends $e{render(){return jt`
      <svg part="base" class="spinner" role="status">
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};ii.styles=si,ii=ut([De("sl-spinner")],ii);class ri extends et{static styles=o`
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
        `}}customElements.define("diagram-element",ri),customElements.define("smry-tbl",class extends Ns{parseMetric(t){const e=t[0].split("|");return z`
            <td rowspan=${t[1]} class="td-colname">
                <abbr title=${e[1]}>${e[0]}</abbr>
            </td>
        `}parseSummaryFunc(t){const[e,s]=t.split("|");return z`
            <td class="td-value">
                ${s?z`<abbr title=${s}>${e}</abbr>`:z`${e}`}
            </td>
        `}async parseSrc(){let t,e=z``;for await(const s of this.makeTextFileLineIterator(this.src)){const i=s.split(";"),r=i[0];if(i.shift(),"H"===r)for(const t of i)e=z`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===r)t=this.parseMetric(i);else{const s=z`${i.map((t=>this.parseSummaryFunc(t)))}`;e=z`
                    ${e}
                    <tr>
                      ${t}
                      ${s}
                    </tr>
                `,t&&(t=void 0)}}return z`<table width=${this.getWidth(this.cols)}>${e}</table>`}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}});class oi extends ei{static styles=o`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},smrytblpath:{type:String}};visibleTemplate(){return z`
            <br>
            <smry-tbl .src="${this.smrytblpath}"></smry-tbl>
            <div class="grid">
                ${this.paths.map((t=>z`
                    <diagram-element path="${t}"></diagram-element>
                `))}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",oi);class ni extends et{static styles=o`
      /*
      * By default, inactive Shoelace tabs have 'display: none' which breaks Plotly
      * legends. Therefore we make inactive tabs invisible in our own way using the
      * following two css classes:
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
    `;static properties={tabFile:{type:String},tabs:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};updated(t){t.has("tabFile")&&fetch(this.tabFile).then((t=>t.json())).then((t=>{this.tabs=t}))}tabTemplate(t){return t.tabs?z`
                <sl-tab-group>
                    ${t.tabs.map((t=>z`
                        <sl-tab slot="nav" panel="${t.name}">${t.name}</sl-tab>
                        <sl-tab-panel class="tab-panel" id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                    `))}
                </sl-tab-group>
        `:z`
            <wult-metric-tab tabname="${t.name}" .smrytblpath="${t.smrytblpath}" .paths="${t.ppaths}" .dir="${t.dir}" ></wult-metric-tab>
        `}render(){return this.tabs?z`
            <sl-tab-group>
                ${this.tabs.map((t=>z`
                    <sl-tab slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
      `:z``}}customElements.define("tab-group",ni);class ai extends et{static properties={src:{type:String},reportInfo:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};async connectedCallback(){super.connectedCallback();try{const t=await fetch(this.src);this.reportInfo=await t.json(),this.toolname=this.reportInfo.toolname,this.titleDescr=this.reportInfo.title_descr,this.tabFile=this.reportInfo.tab_file,this.introtbl=this.reportInfo.intro_tbl}catch(t){t instanceof TypeError&&(this.fetchFailed=!0)}}corsWarning(){return z`
        <sl-alert variant="danger" open>
          Warning: it looks like you might be trying to view this report
          locally.  See our documentation on how to do that <a
          href="https://intel.github.io/wult/pages/howto.html#open-wult-reports-locally">
            here.</a>
          </sl-alert>
      `}render(){return this.fetchFailed?this.corsWarning():z`
            <h1>${this.toolname} report</h1>
            <br>

            ${this.titleDescr?z`
                <p class="title_descr">${this.titleDescr}</p>
                <br>
                `:z``}

            <intro-tbl .src=${this.introtbl}></intro-tbl>
            <br>
            <tab-group .tabFile="${this.tabFile}"></tab-group>
        `}}customElements.define("report-page",ai),es("shoelace")})();