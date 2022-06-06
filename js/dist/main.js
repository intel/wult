/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),s=new Map;class i{constructor(t,s){if(this._$cssResult$=!0,s!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=s.get(this.cssText);return t&&void 0===e&&(s.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const o=t=>new i("string"==typeof t?t:t+"",e),r=(t,...s)=>{const o=1===t.length?t[0]:s.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new i(o,e)},n=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return o(e)})(t):t;var a;const l=window.trustedTypes,h=l?l.emptyScript:"",c=window.reactiveElementPolyfillSupport,d={toAttribute(t,e){switch(e){case Boolean:t=t?h:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},p=(t,e)=>e!==t&&(e==e||t==t),u={attribute:!0,type:String,converter:d,reflect:!1,hasChanged:p};class v extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=u){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const o=this[t];this[e]=i,this.requestUpdate(t,o,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||u}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const s=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{t?e.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const s=document.createElement("style"),i=window.litNonce;void 0!==i&&s.setAttribute("nonce",i),s.textContent=t.cssText,e.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=u){var i,o;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(o=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==o?o:d.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,i,o;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),a=t.converter,l=null!==(o=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==o?o:d.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var b;v.finalized=!0,v.elementProperties=new Map,v.elementStyles=[],v.shadowRootOptions={mode:"open"},null==c||c({ReactiveElement:v}),(null!==(a=globalThis.reactiveElementVersions)&&void 0!==a?a:globalThis.reactiveElementVersions=[]).push("1.3.2");const g=globalThis.trustedTypes,f=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,m=`lit$${(Math.random()+"").slice(9)}$`,y="?"+m,$=`<${y}>`,_=document,w=(t="")=>_.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,x=Array.isArray,C=t=>{var e;return x(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,E=/-->/g,k=/>/g,T=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,U=/'/g,M=/"/g,P=/^(?:script|style|textarea|title)$/i,H=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),N=H(1),O=(H(2),Symbol.for("lit-noChange")),z=Symbol.for("lit-nothing"),L=new WeakMap,R=(t,e,s)=>{var i,o;const r=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=r._$litPart$;if(void 0===n){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;r._$litPart$=n=new W(e.insertBefore(w(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n},B=_.createTreeWalker(_,129,null,!1),I=(t,e)=>{const s=t.length-1,i=[];let o,r=2===e?"<svg>":"",n=S;for(let e=0;e<s;e++){const s=t[e];let a,l,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,l=n.exec(s),null!==l);)c=n.lastIndex,n===S?"!--"===l[1]?n=E:void 0!==l[1]?n=k:void 0!==l[2]?(P.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=T):void 0!==l[3]&&(n=T):n===T?">"===l[0]?(n=null!=o?o:S,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?T:'"'===l[3]?M:U):n===M||n===U?n=T:n===E||n===k?n=S:(n=T,o=void 0);const d=n===T&&t[e+1].startsWith("/>")?" ":"";r+=n===S?s+$:h>=0?(i.push(a),s.slice(0,h)+"$lit$"+s.slice(h)+m+d):s+m+(-2===h?(i.push(void 0),e):d)}const a=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==f?f.createHTML(a):a,i]};class D{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,h]=I(t,e);if(this.el=D.createElement(l,s),B.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=B.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(m)){const s=h[r++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(m),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?q:"?"===e[1]?G:"@"===e[1]?Y:V})}else a.push({type:6,index:o})}for(const e of t)i.removeAttribute(e)}if(P.test(i.tagName)){const t=i.textContent.split(m),e=t.length-1;if(e>0){i.textContent=g?g.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],w()),B.nextNode(),a.push({type:2,index:++o});i.append(t[e],w())}}}else if(8===i.nodeType)if(i.data===y)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=i.data.indexOf(m,t+1));)a.push({type:7,index:o}),t+=m.length-1}o++}}static createElement(t,e){const s=_.createElement("template");return s.innerHTML=t,s}}function F(t,e,s=t,i){var o,r,n,a;if(e===O)return e;let l=void 0!==i?null===(o=s._$Cl)||void 0===o?void 0:o[i]:s._$Cu;const h=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==h&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===h?l=void 0:(l=new h(t),l._$AT(t,s,i)),void 0!==i?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[i]=l:s._$Cu=l),void 0!==l&&(e=F(t,l._$AS(t,e.values),l,i)),e}class j{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:_).importNode(s,!0);B.currentNode=o;let r=B.nextNode(),n=0,a=0,l=i[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new W(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new Z(r,this,t)),this.v.push(e),l=i[++a]}n!==(null==l?void 0:l.index)&&(r=B.nextNode(),n++)}return o}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class W{constructor(t,e,s,i){var o;this.type=2,this._$AH=z,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(o=null==i?void 0:i.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=F(this,t,e),A(t)?t===z||null==t||""===t?(this._$AH!==z&&this._$AR(),this._$AH=z):t!==this._$AH&&t!==O&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):C(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==z&&A(this._$AH)?this._$AA.nextSibling.data=t:this.k(_.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,o="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=D.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(s);else{const t=new j(o,this),e=t.p(this.options);t.m(s),this.k(e),this._$AH=t}}_$AC(t){let e=L.get(t.strings);return void 0===e&&L.set(t.strings,e=new D(t)),e}S(t){x(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const o of t)i===e.length?e.push(s=new W(this.M(w()),this.M(w()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class V{constructor(t,e,s,i,o){this.type=1,this._$AH=z,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=z}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const o=this.strings;let r=!1;if(void 0===o)t=F(this,t,e,0),r=!A(t)||t!==this._$AH&&t!==O,r&&(this._$AH=t);else{const i=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=F(this,i[s+n],e,n),a===O&&(a=this._$AH[n]),r||(r=!A(a)||a!==this._$AH[n]),a===z?t=z:t!==z&&(t+=(null!=a?a:"")+o[n+1]),this._$AH[n]=a}r&&!i&&this.C(t)}C(t){t===z?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class q extends V{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===z?void 0:t}}const K=g?g.emptyScript:"";class G extends V{constructor(){super(...arguments),this.type=4}C(t){t&&t!==z?this.element.setAttribute(this.name,K):this.element.removeAttribute(this.name)}}class Y extends V{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=F(this,t,e,0))&&void 0!==s?s:z)===O)return;const i=this._$AH,o=t===z&&i!==z||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==z&&(i===z||o);o&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}}class Z{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){F(this,t)}}const J={L:"$lit$",P:m,V:y,I:1,N:I,R:j,j:C,D:F,H:W,F:V,O:G,W:Y,B:q,Z},Q=window.litHtmlPolyfillSupport;var X,tt;null==Q||Q(D,W),(null!==(b=globalThis.litHtmlVersions)&&void 0!==b?b:globalThis.litHtmlVersions=[]).push("2.2.5");class et extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=R(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return O}}et.finalized=!0,et._$litElement$=!0,null===(X=globalThis.litElementHydrateSupport)||void 0===X||X.call(globalThis,{LitElement:et});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:et}),(null!==(tt=globalThis.litElementVersions)&&void 0!==tt?tt:globalThis.litElementVersions=[]).push("3.2.0"),Object.create;var it=Object.defineProperty,ot=Object.defineProperties,rt=Object.getOwnPropertyDescriptor,nt=Object.getOwnPropertyDescriptors,at=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),lt=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),ht=Object.prototype.propertyIsEnumerable,ct=(t,e,s)=>e in t?it(t,e,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[e]=s,dt=(t,e)=>{for(var s in e||(e={}))lt.call(e,s)&&ct(t,s,e[s]);if(at)for(var s of at(e))ht.call(e,s)&&ct(t,s,e[s]);return t},pt=(t,e)=>ot(t,nt(e)),ut=(t,e,s,i)=>{for(var o,r=i>1?void 0:i?rt(e,s):e,n=t.length-1;n>=0;n--)(o=t[n])&&(r=(i?o(e,s,r):o(r))||r);return i&&r&&it(e,s,r),r};function vt(t,e,s){return new Promise((i=>{if((null==s?void 0:s.duration)===1/0)throw new Error("Promise-based animations must be finite.");const o=t.animate(e,pt(dt({},s),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:s.duration}));o.addEventListener("cancel",i,{once:!0}),o.addEventListener("finish",i,{once:!0})}))}function bt(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const s=requestAnimationFrame(e);t.addEventListener("cancel",(()=>s),{once:!0}),t.addEventListener("finish",(()=>s),{once:!0}),t.cancel()})))))}function gt(t,e){return t.map((t=>pt(dt({},t),{height:"auto"===t.height?`${e}px`:t.height})))}var ft=new Map,mt=new WeakMap;function yt(t,e){ft.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function $t(t,e){const s=mt.get(t);if(null==s?void 0:s[e])return s[e];return ft.get(e)||{keyframes:[],options:{duration:0}}}var _t,wt,At=t=>(...e)=>({_$litDirective$:t,values:e}),xt=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},Ct=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,St=Symbol(),Et=new Map,kt=class{constructor(t,e){if(this._$cssResult$=!0,e!==St)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=Et.get(this.cssText);return Ct&&void 0===t&&(Et.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},Tt=t=>new kt("string"==typeof t?t:t+"",St),Ut=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new kt(s,St)},Mt=Ct?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return Tt(e)})(t):t,Pt=window.trustedTypes,Ht=Pt?Pt.emptyScript:"",Nt=window.reactiveElementPolyfillSupport,Ot={toAttribute(t,e){switch(e){case Boolean:t=t?Ht:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},zt=(t,e)=>e!==t&&(e==e||t==t),Lt={attribute:!0,type:String,converter:Ot,reflect:!1,hasChanged:zt},Rt=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=Lt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const o=this[t];this[e]=i,this.requestUpdate(t,o,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Lt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(Mt(t))}else void 0!==t&&e.push(Mt(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,Ct?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=Lt){var i,o;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(o=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==o?o:Ot.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,i,o;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),a=t.converter,l=null!==(o=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==o?o:Ot.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||zt)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}};Rt.finalized=!0,Rt.elementProperties=new Map,Rt.elementStyles=[],Rt.shadowRootOptions={mode:"open"},null==Nt||Nt({ReactiveElement:Rt}),(null!==(_t=globalThis.reactiveElementVersions)&&void 0!==_t?_t:globalThis.reactiveElementVersions=[]).push("1.3.2");var Bt=globalThis.trustedTypes,It=Bt?Bt.createPolicy("lit-html",{createHTML:t=>t}):void 0,Dt=`lit$${(Math.random()+"").slice(9)}$`,Ft="?"+Dt,jt=`<${Ft}>`,Wt=document,Vt=(t="")=>Wt.createComment(t),qt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Kt=Array.isArray,Gt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Yt=/-->/g,Zt=/>/g,Jt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,Qt=/'/g,Xt=/"/g,te=/^(?:script|style|textarea|title)$/i,ee=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),se=ee(1),ie=ee(2),oe=Symbol.for("lit-noChange"),re=Symbol.for("lit-nothing"),ne=new WeakMap,ae=Wt.createTreeWalker(Wt,129,null,!1),le=class{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,h]=((t,e)=>{const s=t.length-1,i=[];let o,r=2===e?"<svg>":"",n=Gt;for(let e=0;e<s;e++){const s=t[e];let a,l,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,l=n.exec(s),null!==l);)c=n.lastIndex,n===Gt?"!--"===l[1]?n=Yt:void 0!==l[1]?n=Zt:void 0!==l[2]?(te.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=Jt):void 0!==l[3]&&(n=Jt):n===Jt?">"===l[0]?(n=null!=o?o:Gt,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Jt:'"'===l[3]?Xt:Qt):n===Xt||n===Qt?n=Jt:n===Yt||n===Zt?n=Gt:(n=Jt,o=void 0);const d=n===Jt&&t[e+1].startsWith("/>")?" ":"";r+=n===Gt?s+jt:h>=0?(i.push(a),s.slice(0,h)+"$lit$"+s.slice(h)+Dt+d):s+Dt+(-2===h?(i.push(void 0),e):d)}const a=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==It?It.createHTML(a):a,i]})(t,e);if(this.el=le.createElement(l,s),ae.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=ae.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(Dt)){const s=h[r++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(Dt),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?ve:"?"===e[1]?ge:"@"===e[1]?fe:ue})}else a.push({type:6,index:o})}for(const e of t)i.removeAttribute(e)}if(te.test(i.tagName)){const t=i.textContent.split(Dt),e=t.length-1;if(e>0){i.textContent=Bt?Bt.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],Vt()),ae.nextNode(),a.push({type:2,index:++o});i.append(t[e],Vt())}}}else if(8===i.nodeType)if(i.data===Ft)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=i.data.indexOf(Dt,t+1));)a.push({type:7,index:o}),t+=Dt.length-1}o++}}static createElement(t,e){const s=Wt.createElement("template");return s.innerHTML=t,s}};function he(t,e,s=t,i){var o,r,n,a;if(e===oe)return e;let l=void 0!==i?null===(o=s._$Cl)||void 0===o?void 0:o[i]:s._$Cu;const h=qt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==h&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===h?l=void 0:(l=new h(t),l._$AT(t,s,i)),void 0!==i?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[i]=l:s._$Cu=l),void 0!==l&&(e=he(t,l._$AS(t,e.values),l,i)),e}var ce,de,pe=class{constructor(t,e,s,i){var o;this.type=2,this._$AH=re,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(o=null==i?void 0:i.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=he(this,t,e),qt(t)?t===re||null==t||""===t?(this._$AH!==re&&this._$AR(),this._$AH=re):t!==this._$AH&&t!==oe&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):(t=>{var e;return Kt(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==re&&qt(this._$AH)?this._$AA.nextSibling.data=t:this.k(Wt.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,o="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=le.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(s);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Wt).importNode(s,!0);ae.currentNode=o;let r=ae.nextNode(),n=0,a=0,l=i[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new pe(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new me(r,this,t)),this.v.push(e),l=i[++a]}n!==(null==l?void 0:l.index)&&(r=ae.nextNode(),n++)}return o}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}(o,this),e=t.p(this.options);t.m(s),this.k(e),this._$AH=t}}_$AC(t){let e=ne.get(t.strings);return void 0===e&&ne.set(t.strings,e=new le(t)),e}S(t){Kt(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const o of t)i===e.length?e.push(s=new pe(this.M(Vt()),this.M(Vt()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},ue=class{constructor(t,e,s,i,o){this.type=1,this._$AH=re,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=re}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const o=this.strings;let r=!1;if(void 0===o)t=he(this,t,e,0),r=!qt(t)||t!==this._$AH&&t!==oe,r&&(this._$AH=t);else{const i=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=he(this,i[s+n],e,n),a===oe&&(a=this._$AH[n]),r||(r=!qt(a)||a!==this._$AH[n]),a===re?t=re:t!==re&&(t+=(null!=a?a:"")+o[n+1]),this._$AH[n]=a}r&&!i&&this.C(t)}C(t){t===re?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},ve=class extends ue{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===re?void 0:t}},be=Bt?Bt.emptyScript:"",ge=class extends ue{constructor(){super(...arguments),this.type=4}C(t){t&&t!==re?this.element.setAttribute(this.name,be):this.element.removeAttribute(this.name)}},fe=class extends ue{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=he(this,t,e,0))&&void 0!==s?s:re)===oe)return;const i=this._$AH,o=t===re&&i!==re||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==re&&(i===re||o);o&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}},me=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){he(this,t)}},ye=window.litHtmlPolyfillSupport;null==ye||ye(le,pe),(null!==(wt=globalThis.litHtmlVersions)&&void 0!==wt?wt:globalThis.litHtmlVersions=[]).push("2.2.4");var $e=class extends Rt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,s)=>{var i,o;const r=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=r._$litPart$;if(void 0===n){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;r._$litPart$=n=new pe(e.insertBefore(Vt(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return oe}};$e.finalized=!0,$e._$litElement$=!0,null===(ce=globalThis.litElementHydrateSupport)||void 0===ce||ce.call(globalThis,{LitElement:$e});var _e=globalThis.litElementPolyfillSupport;null==_e||_e({LitElement:$e}),(null!==(de=globalThis.litElementVersions)&&void 0!==de?de:globalThis.litElementVersions=[]).push("3.2.0");var we=At(class extends xt{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var s,i;if(void 0===this.et){this.et=new Set,void 0!==t.strings&&(this.st=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(s=this.st)||void 0===s?void 0:s.has(t))&&this.et.add(t);return this.render(e)}const o=t.element.classList;this.et.forEach((t=>{t in e||(o.remove(t),this.et.delete(t))}));for(const t in e){const s=!!e[t];s===this.et.has(t)||(null===(i=this.st)||void 0===i?void 0:i.has(t))||(s?(o.add(t),this.et.add(t)):(o.remove(t),this.et.delete(t)))}return oe}}),Ae=Ut`
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
`,xe=Ut`
  ${Ae}

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
`;function Ce(t,e){const s=dt({waitUntilFirstUpdate:!1},e);return(e,i)=>{const{update:o}=e;if(t in e){const r=t;e.update=function(t){if(t.has(r)){const e=t.get(r),o=this[r];e!==o&&(s.waitUntilFirstUpdate&&!this.hasUpdated||this[i](e,o))}o.call(this,t)}}}}function Se(t,e,s){const i=new CustomEvent(e,dt({bubbles:!0,cancelable:!1,composed:!0,detail:{}},s));return t.dispatchEvent(i),i}function Ee(t,e){return new Promise((s=>{t.addEventListener(e,(function i(o){o.target===t&&(t.removeEventListener(e,i),s())}))}))}var ke=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:s,elements:i}=e;return{kind:s,elements:i,finisher(e){window.customElements.define(t,e)}}})(t,e),Te=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?pt(dt({},e),{finisher(s){s.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(s){s.createProperty(e.key,t)}};function Ue(t){return(e,s)=>void 0!==s?((t,e,s)=>{e.constructor.createProperty(s,t)})(t,e,s):Te(t,e)}function Me(t){return Ue(pt(dt({},t),{state:!0}))}var Pe;function He(t,e){return(({finisher:t,descriptor:e})=>(s,i)=>{var o;if(void 0===i){const i=null!==(o=s.originalKey)&&void 0!==o?o:s.key,r=null!=e?{kind:"method",placement:"prototype",key:i,descriptor:e(s.key)}:pt(dt({},s),{key:i});return null!=t&&(r.finisher=function(e){t(e,i)}),r}{const o=s.constructor;void 0!==e&&Object.defineProperty(s,i,e(i)),null==t||t(o,i)}})({descriptor:s=>{const i={get(){var e,s;return null!==(s=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==s?s:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof s?Symbol():"__"+s;i.get=function(){var s,i;return void 0===this[e]&&(this[e]=null!==(i=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(t))&&void 0!==i?i:null),this[e]}}return i}})}null===(Pe=window.HTMLSlotElement)||void 0===Pe||Pe.prototype.assignedElements;var Ne=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Oe=class extends $e{constructor(){super(...arguments),this.hasSlotController=new class{constructor(t,...e){this.slotNames=[],(this.host=t).addController(this),this.slotNames=e,this.handleSlotChange=this.handleSlotChange.bind(this)}hasDefaultSlot(){return[...this.host.childNodes].some((t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1}))}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}handleSlotChange(t){const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()}}(this,"icon","suffix"),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,Ee(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Ee(this,"sl-after-hide")}async toast(){return new Promise((t=>{null===Ne.parentElement&&document.body.append(Ne),Ne.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{Ne.removeChild(this),t(),null===Ne.querySelector("sl-alert")&&Ne.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){Se(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await bt(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=$t(this,"alert.show");await vt(this.base,t,e),Se(this,"sl-after-show")}else{Se(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await bt(this.base);const{keyframes:t,options:e}=$t(this,"alert.hide");await vt(this.base,t,e),this.base.hidden=!0,Se(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return se`
      <div
        part="base"
        class=${we({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--has-icon":this.hasSlotController.test("icon"),"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
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
    `}};Oe.styles=xe,ut([He('[part="base"]')],Oe.prototype,"base",2),ut([Ue({type:Boolean,reflect:!0})],Oe.prototype,"open",2),ut([Ue({type:Boolean,reflect:!0})],Oe.prototype,"closable",2),ut([Ue({reflect:!0})],Oe.prototype,"variant",2),ut([Ue({type:Number})],Oe.prototype,"duration",2),ut([Ce("open",{waitUntilFirstUpdate:!0})],Oe.prototype,"handleOpenChange",1),ut([Ce("duration")],Oe.prototype,"handleDurationChange",1),Oe=ut([ke("sl-alert")],Oe),yt("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),yt("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var ze=(()=>{const t=document.createElement("style");let e;try{document.head.appendChild(t),t.sheet.insertRule(":focus-visible { color: inherit }"),e=!0}catch(t){e=!1}finally{t.remove()}return e})(),Le=Tt(ze?":focus-visible":":focus"),Re=Ut`
  ${Ae}

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

  .icon-button${Le} {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }
`,Be=Symbol.for(""),Ie=t=>{var e,s;if((null===(e=t)||void 0===e?void 0:e.r)===Be)return null===(s=t)||void 0===s?void 0:s._$litStatic$},De=(t,...e)=>({_$litStatic$:e.reduce(((e,s,i)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(s)+t[i+1]),t[0]),r:Be}),Fe=new Map,je=t=>(e,...s)=>{const i=s.length;let o,r;const n=[],a=[];let l,h=0,c=!1;for(;h<i;){for(l=e[h];h<i&&void 0!==(r=s[h],o=Ie(r));)l+=o+e[++h],c=!0;a.push(r),n.push(l),h++}if(h===i&&n.push(e[i]),c){const t=n.join("$$lit$$");void 0===(e=Fe.get(t))&&(n.raw=n,Fe.set(t,e=n)),s=a}return t(e,...s)},We=je(se),Ve=(je(ie),t=>null!=t?t:re),qe=class extends $e{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Se(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Se(this,"sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}render(){const t=!!this.href,e=t?De`a`:De`button`;return We`
      <${e}
        part="base"
        class=${we({"icon-button":!0,"icon-button--disabled":!t&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${Ve(t?void 0:this.disabled)}
        type=${Ve(t?void 0:"button")}
        href=${Ve(t?this.href:void 0)}
        target=${Ve(t?this.target:void 0)}
        download=${Ve(t?this.download:void 0)}
        rel=${Ve(t&&this.target?"noreferrer noopener":void 0)}
        role=${Ve(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          name=${Ve(this.name)}
          library=${Ve(this.library)}
          src=${Ve(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${e}>
    `}};qe.styles=Re,ut([Me()],qe.prototype,"hasFocus",2),ut([He(".icon-button")],qe.prototype,"button",2),ut([Ue()],qe.prototype,"name",2),ut([Ue()],qe.prototype,"library",2),ut([Ue()],qe.prototype,"src",2),ut([Ue()],qe.prototype,"href",2),ut([Ue()],qe.prototype,"target",2),ut([Ue()],qe.prototype,"download",2),ut([Ue()],qe.prototype,"label",2),ut([Ue({type:Boolean,reflect:!0})],qe.prototype,"disabled",2),qe=ut([ke("sl-icon-button")],qe);var Ke="";function Ge(t){Ke=t}var Ye=[...document.getElementsByTagName("script")],Ze=Ye.find((t=>t.hasAttribute("data-shoelace")));if(Ze)Ge(Ze.getAttribute("data-shoelace"));else{const t=Ye.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let e="";t&&(e=t.getAttribute("src")),Ge(e.split("/").slice(0,-1).join("/"))}var Je={"check-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">\n      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"></path>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},Qe=[{name:"default",resolver:t=>`${Ke.replace(/\/$/,"")}/assets/icons/${t}.svg`},{name:"system",resolver:t=>t in Je?`data:image/svg+xml,${encodeURIComponent(Je[t])}`:""}],Xe=[];function ts(t){return Qe.find((e=>e.name===t))}var es=new Map,ss=new Map;var is=Ut`
  ${Ae}

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
`,os=class extends xt{constructor(t){if(super(t),this.it=re,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===re||null==t)return this.ft=void 0,this.it=t;if(t===oe)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.ft;this.it=t;const e=[t];return e.raw=e,this.ft={_$litType$:this.constructor.resultType,strings:e,values:[]}}};os.directiveName="unsafeHTML",os.resultType=1,At(os);var rs=class extends os{};rs.directiveName="unsafeSVG",rs.resultType=2;var ns=At(rs),as=new DOMParser,ls=class extends $e{constructor(){super(...arguments),this.svg="",this.label="",this.library="default"}connectedCallback(){super.connectedCallback(),Xe.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,Xe=Xe.filter((e=>e!==t))}getUrl(){const t=ts(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){var t;const e=ts(this.library),s=this.getUrl();if(s)try{const i=await async function(t){if(ss.has(t))return ss.get(t);const e=await function(t,e="cors"){if(es.has(t))return es.get(t);const s=fetch(t,{mode:e}).then((async t=>({ok:t.ok,status:t.status,html:await t.text()})));return es.set(t,s),s}(t),s={ok:e.ok,status:e.status,svg:null};if(e.ok){const t=document.createElement("div");t.innerHTML=e.html;const i=t.firstElementChild;s.svg="svg"===(null==i?void 0:i.tagName.toLowerCase())?i.outerHTML:""}return ss.set(t,s),s}(s);if(s!==this.getUrl())return;if(i.ok){const s=as.parseFromString(i.svg,"text/html").body.querySelector("svg");null!==s?(null==(t=null==e?void 0:e.mutator)||t.call(e,s),this.svg=s.outerHTML,Se(this,"sl-load")):(this.svg="",Se(this,"sl-error"))}else this.svg="",Se(this,"sl-error")}catch(t){Se(this,"sl-error")}else this.svg.length>0&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return se` <div
      part="base"
      class="icon"
      role=${Ve(t?"img":void 0)}
      aria-label=${Ve(t?this.label:void 0)}
      aria-hidden=${Ve(t?void 0:"true")}
    >
      ${ns(this.svg)}
    </div>`}};ls.styles=is,ut([Me()],ls.prototype,"svg",2),ut([Ue({reflect:!0})],ls.prototype,"name",2),ut([Ue()],ls.prototype,"src",2),ut([Ue()],ls.prototype,"label",2),ut([Ue({reflect:!0})],ls.prototype,"library",2),ut([Ce("name"),Ce("src"),Ce("library")],ls.prototype,"setIcon",1),ls=ut([ke("sl-icon")],ls);const hs=t=>(...e)=>({_$litDirective$:t,values:e});class cs{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const{H:ds}=J,ps=(t,e)=>{var s,i;return void 0===e?void 0!==(null===(s=t)||void 0===s?void 0:s._$litType$):(null===(i=t)||void 0===i?void 0:i._$litType$)===e},us=()=>document.createComment(""),vs=(t,e,s)=>{var i;const o=t._$AA.parentNode,r=void 0===e?t._$AB:e._$AA;if(void 0===s){const e=o.insertBefore(us(),r),i=o.insertBefore(us(),r);s=new ds(e,i,t,t.options)}else{const e=s._$AB.nextSibling,n=s._$AM,a=n!==t;if(a){let e;null===(i=s._$AQ)||void 0===i||i.call(s,t),s._$AM=t,void 0!==s._$AP&&(e=t._$AU)!==n._$AU&&s._$AP(e)}if(e!==r||a){let t=s._$AA;for(;t!==e;){const e=t.nextSibling;o.insertBefore(t,r),t=e}}}return s},bs={},gs=(t,e=bs)=>t._$AH=e,fs=t=>t._$AH,ms=(t,e)=>{var s,i;const o=t._$AN;if(void 0===o)return!1;for(const t of o)null===(i=(s=t)._$AO)||void 0===i||i.call(s,e,!1),ms(t,e);return!0},ys=t=>{let e,s;do{if(void 0===(e=t._$AM))break;s=e._$AN,s.delete(t),t=e}while(0===(null==s?void 0:s.size))},$s=t=>{for(let e;e=t._$AM;t=e){let s=e._$AN;if(void 0===s)e._$AN=s=new Set;else if(s.has(t))break;s.add(t),As(e)}};function _s(t){void 0!==this._$AN?(ys(this),this._$AM=t,$s(this)):this._$AM=t}function ws(t,e=!1,s=0){const i=this._$AH,o=this._$AN;if(void 0!==o&&0!==o.size)if(e)if(Array.isArray(i))for(let t=s;t<i.length;t++)ms(i[t],!1),ys(i[t]);else null!=i&&(ms(i,!1),ys(i));else ms(this,t)}const As=t=>{var e,s,i,o;2==t.type&&(null!==(e=(i=t)._$AP)&&void 0!==e||(i._$AP=ws),null!==(s=(o=t)._$AQ)&&void 0!==s||(o._$AQ=_s))};class xs extends cs{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,s){super._$AT(t,e,s),$s(this),this.isConnected=t._$AU}_$AO(t,e=!0){var s,i;t!==this.isConnected&&(this.isConnected=t,t?null===(s=this.reconnected)||void 0===s||s.call(this):null===(i=this.disconnected)||void 0===i||i.call(this)),e&&(ms(this,t),ys(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Cs{constructor(t){this.U=t}disconnect(){this.U=void 0}reconnect(t){this.U=t}deref(){return this.U}}class Ss{constructor(){this.Y=void 0,this.q=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Y=this.q=void 0}}const Es=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,ks=hs(class extends xs{constructor(){super(...arguments),this._$Cwt=1073741823,this._$Cyt=[],this._$CG=new Cs(this),this._$CK=new Ss}render(...t){var e;return null!==(e=t.find((t=>!Es(t))))&&void 0!==e?e:O}update(t,e){const s=this._$Cyt;let i=s.length;this._$Cyt=e;const o=this._$CG,r=this._$CK;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cwt);t++){const n=e[t];if(!Es(n))return this._$Cwt=t,n;t<i&&n===s[t]||(this._$Cwt=1073741823,i=0,Promise.resolve(n).then((async t=>{for(;r.get();)await r.get();const e=o.deref();if(void 0!==e){const s=e._$Cyt.indexOf(n);s>-1&&s<e._$Cwt&&(e._$Cwt=s,e.setValue(t))}})))}return O}disconnected(){this._$CG.disconnect(),this._$CK.pause()}reconnected(){this._$CG.reconnect(this),this._$CK.resume()}});class Ts{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class Us extends et{static properties={src:{type:String},template:{attribute:!1}};static styles=r`
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
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),s=(await fetch(t)).body.getReader();let{value:i,done:o}=await s.read();i=i?e.decode(i,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(i);if(t)yield i.substring(n,t.index),n=r.lastIndex;else{if(o)break;const t=i.substr(n);({value:i,done:o}=await s.read()),i=t+(i?e.decode(i,{stream:!0}):""),n=r.lastIndex=0}}n<i.length&&(yield i.substr(n))}render(){if(!this.src)return N``;const t=this.parseSrc();return N`${ks(t,N``)}`}}customElements.define("report-table",Us),customElements.define("intro-tbl",class extends Us{parseHeader(t){const e=t.split(";");return N`
            <tr>
                ${e.map((t=>N`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=N``,s=!0;for(const i of t.split(";")){const[t,o,r]=i.split("|");let n=N`${t}`;r&&(n=N`<a href=${r}>${n}</a>`),o&&(n=N`<abbr title=${o}>${n}</abbr>`),s?(e=N`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,s=!1):e=N`${e}
                    <td>
                        ${n}
                    </td>
                `}return N`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.src);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Ts("first line in intro table file should be a header.");e=e.slice(2);let s=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Ts("lines following the first should all be normal table rows.");e=e.slice(2),s=N`${s}${this.parseRow(e)}`}return N`<table>${s}</table>`}});var Ms=Ut`
  ${Ae}

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
`;function Ps(t,e,s="vertical",i="smooth"){const o=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=o.top+e.scrollTop,n=o.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,h=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==s&&"both"!==s||(n<a?e.scrollTo({left:n,behavior:i}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:i})),"vertical"!==s&&"both"!==s||(r<h?e.scrollTo({top:r,behavior:i}):r+t.clientHeight>c&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:i}))}var Hs,Ns=new Set,Os=new MutationObserver(Rs),zs=new Map,Ls=document.documentElement.lang||navigator.language;function Rs(){Ls=document.documentElement.lang||navigator.language,[...Ns.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}Os.observe(document.documentElement,{attributes:!0,attributeFilter:["lang"]});var Bs=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Ns.add(this.host)}hostDisconnected(){Ns.delete(this.host)}term(t,...e){return function(t,e,...s){const i=t.toLowerCase().slice(0,2),o=t.length>2?t.toLowerCase():"",r=zs.get(o),n=zs.get(i);let a;if(r&&r[e])a=r[e];else if(n&&n[e])a=n[e];else{if(!Hs||!Hs[e])return console.error(`No translation found for: ${e}`),e;a=Hs[e]}return"function"==typeof a?a(...s):a}(this.host.lang||Ls,t,...e)}date(t,e){return function(t,e,s){return e=new Date(e),new Intl.DateTimeFormat(t,s).format(e)}(this.host.lang||Ls,t,e)}number(t,e){return function(t,e,s){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(t,s).format(e)}(this.host.lang||Ls,t,e)}relativeTime(t,e,s){return function(t,e,s,i){return new Intl.RelativeTimeFormat(t,i).format(e,s)}(this.host.lang||Ls,t,e,s)}};!function(...t){t.map((t=>{const e=t.$code.toLowerCase();zs.set(e,t),Hs||(Hs=t)})),Rs()}({$code:"en",$name:"English",$dir:"ltr",clearEntry:"Clear entry",close:"Close",copy:"Copy",currentValue:"Current value",hidePassword:"Hide password",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",toggleColorFormat:"Toggle color format"});var Is=class extends $e{constructor(){super(...arguments),this.localize=new Bs(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{var s;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(s=this.getActiveTab())?s:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t=!1){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement;if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&"ArrowLeft"===t.key||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s--:(["top","bottom"].includes(this.placement)&&"ArrowRight"===t.key||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&s++,s<0&&(s=this.tabs.length-1),s>this.tabs.length-1&&(s=0),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Ps(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth}setActiveTab(t,e){if(e=dt({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const s=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)})),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Ps(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(s&&Se(this,"sl-tab-hide",{detail:{name:s.panel}}),Se(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,s=t.clientHeight,i=this.getAllTabs(!0),o=i.slice(0,i.indexOf(t)).reduce(((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight})),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=`translateX(${o.left}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${s}px`,this.indicator.style.transform=`translateY(${o.top}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.panels=this.getAllPanels(),this.syncIndicator()}render(){return se`
      <div
        part="base"
        class=${we({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--has-scroll-controls":this.hasScrollControls})}
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
    `}};Is.styles=Ms,ut([He(".tab-group")],Is.prototype,"tabGroup",2),ut([He(".tab-group__body")],Is.prototype,"body",2),ut([He(".tab-group__nav")],Is.prototype,"nav",2),ut([He(".tab-group__indicator")],Is.prototype,"indicator",2),ut([Me()],Is.prototype,"hasScrollControls",2),ut([Ue()],Is.prototype,"placement",2),ut([Ue()],Is.prototype,"activation",2),ut([Ue({attribute:"no-scroll-controls",type:Boolean})],Is.prototype,"noScrollControls",2),ut([Ue()],Is.prototype,"lang",2),ut([Ce("noScrollControls",{waitUntilFirstUpdate:!0})],Is.prototype,"updateScrollControls",1),ut([Ce("placement",{waitUntilFirstUpdate:!0})],Is.prototype,"syncIndicator",1),Is=ut([ke("sl-tab-group")],Is);var Ds=0;function Fs(){return++Ds}var js=Ut`
  ${Ae}

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

  .tab${Le}:not(.tab--disabled) {
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
`,Ws=class extends $e{constructor(){super(...arguments),this.localize=new Bs(this),this.attrId=Fs(),this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Se(this,"sl-close")}render(){return this.id=this.id.length>0?this.id:this.componentId,se`
      <div
        part="base"
        class=${we({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
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
    `}};Ws.styles=js,ut([He(".tab")],Ws.prototype,"tab",2),ut([Ue({reflect:!0})],Ws.prototype,"panel",2),ut([Ue({type:Boolean,reflect:!0})],Ws.prototype,"active",2),ut([Ue({type:Boolean})],Ws.prototype,"closable",2),ut([Ue({type:Boolean,reflect:!0})],Ws.prototype,"disabled",2),ut([Ue()],Ws.prototype,"lang",2),Ws=ut([ke("sl-tab")],Ws);var Vs=Ut`
  ${Ae}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }
`,qs=class extends $e{constructor(){super(...arguments),this.attrId=Fs(),this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId}render(){return this.style.display=this.active?"block":"none",se`
      <div part="base" class="tab-panel" role="tabpanel" aria-hidden=${this.active?"false":"true"}>
        <slot></slot>
      </div>
    `}};qs.styles=Vs,ut([Ue({reflect:!0})],qs.prototype,"name",2),ut([Ue({type:Boolean,reflect:!0})],qs.prototype,"active",2),qs=ut([ke("sl-tab-panel")],qs);const Ks=hs(class extends cs{constructor(t){super(t),this.tt=new WeakMap}render(t){return[t]}update(t,[e]){if(ps(this.it)&&(!ps(e)||this.it.strings!==e.strings)){const e=fs(t).pop();let s=this.tt.get(this.it.strings);if(void 0===s){const t=document.createDocumentFragment();s=R(z,t),s.setConnected(!1),this.tt.set(this.it.strings,s)}gs(s,[e]),vs(s,void 0,e)}if(ps(e)){if(!ps(this.it)||this.it.strings!==e.strings){const s=this.tt.get(e.strings);if(void 0!==s){const e=fs(s).pop();(t=>{t._$AR()})(t),vs(t,void 0,e),gs(t,[e])}}this.it=e}else this.it=void 0;return this.render(e)}});class Gs extends et{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(t,e){for(const e of t)"active"===e.attributeName&&(this.tabname===e.target.id?this.visible=!0:this.visible=!1)}connectedCallback(){super.connectedCallback();const t=this.checkVisible.bind(this);this.observer=new MutationObserver(t),this.observer.observe(this.parentElement,{attributes:!0})}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return N`
        ${Ks(this.visible?N`${this.visibleTemplate()}`:N``)}`}}customElements.define("wult-tab",Gs);var Ys=Ut`
  ${Ae}

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
`,Zs=class extends $e{render(){return se`
      <svg part="base" class="spinner" role="status">
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};Zs.styles=Ys,Zs=ut([ke("sl-spinner")],Zs);class Js extends et{static styles=r`
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
  `;static properties={path:{type:String}};hideLoading(){this.renderRoot.querySelector("#loading").style.display="none"}render(){return N`
            <div id="loading" class="loading">
                <sl-spinner></sl-spinner>
            </div>
            <div class="plot">
                <iframe @load=${this.hideLoading} seamless frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
            </div>
        `}}customElements.define("diagram-element",Js);var Qs=Ut`
  ${Ae}

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

  .details__header${Le} {
    outline: var(--sl-focus-ring);
    outline-offset: calc(1px + var(--sl-focus-ring-offset));
  }

  .details--disabled .details__header {
    cursor: not-allowed;
  }

  .details--disabled .details__header${Le} {
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
`,Xs=class extends $e{constructor(){super(...arguments),this.open=!1,this.disabled=!1}firstUpdated(){this.body.hidden=!this.open,this.body.style.height=this.open?"auto":"0"}async show(){if(!this.open&&!this.disabled)return this.open=!0,Ee(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,Ee(this,"sl-after-hide")}handleSummaryClick(){this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){Se(this,"sl-show"),await bt(this.body),this.body.hidden=!1;const{keyframes:t,options:e}=$t(this,"details.show");await vt(this.body,gt(t,this.body.scrollHeight),e),this.body.style.height="auto",Se(this,"sl-after-show")}else{Se(this,"sl-hide"),await bt(this.body);const{keyframes:t,options:e}=$t(this,"details.hide");await vt(this.body,gt(t,this.body.scrollHeight),e),this.body.hidden=!0,this.body.style.height="auto",Se(this,"sl-after-hide")}}render(){return se`
      <div
        part="base"
        class=${we({details:!0,"details--open":this.open,"details--disabled":this.disabled})}
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
    `}};Xs.styles=Qs,ut([He(".details")],Xs.prototype,"details",2),ut([He(".details__header")],Xs.prototype,"header",2),ut([He(".details__body")],Xs.prototype,"body",2),ut([Ue({type:Boolean,reflect:!0})],Xs.prototype,"open",2),ut([Ue()],Xs.prototype,"summary",2),ut([Ue({type:Boolean,reflect:!0})],Xs.prototype,"disabled",2),ut([Ce("open",{waitUntilFirstUpdate:!0})],Xs.prototype,"handleOpenChange",1),Xs=ut([ke("sl-details")],Xs),yt("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),yt("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}});class ti extends Us{static styles=[Us.styles,r`
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
        `];parseMetric(t){const e=t[0].split("|");return N`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,s]=t.split("|");return N`
            <td class="td-value">
                ${s?N`<abbr title=${s}>${e}</abbr>`:N`${e}`}
            </td>
        `}async parseSrc(){let t,e=N``;for await(const s of this.makeTextFileLineIterator(this.src)){const i=s.split(";"),o=i[0];if(i.shift(),"H"===o)for(const t of i)e=N`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===o)t=this.parseMetric(i);else{const s=N`${i.map((t=>this.parseSummaryFunc(t)))}`;e=N`
                    ${e}
                    <tr>
                      ${t}
                      ${s}
                    </tr>
                `,t&&(t=void 0)}}return N`<table width=${this.getWidth(this.cols)}>${e}</table>`}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}}customElements.define("smry-tbl",ti);class ei extends Gs{static styles=r`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},smrytblpath:{type:String}};visibleTemplate(){return N`
            <br>
            <smry-tbl .src="${this.smrytblpath}"></smry-tbl>
            <div class="grid">
                ${this.paths.map((t=>N`
                    <diagram-element path="${t}"></diagram-element>
                `))}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",ei);class si extends et{static styles=r`
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
    `;static properties={tabFile:{type:String},tabs:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};updated(t){t.has("tabFile")&&fetch(this.tabFile).then((t=>t.json())).then((t=>{this.tabs=t}))}tabTemplate(t){return t.tabs?N`
                <sl-tab-group>
                    ${t.tabs.map((t=>N`
                        <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                        <sl-tab-panel class="tab-panel" id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                    `))}
                </sl-tab-group>
        `:N`
            <wult-metric-tab tabname="${t.name}" .smrytblpath="${t.smrytblpath}" .paths="${t.ppaths}" .dir="${t.dir}" ></wult-metric-tab>
        `}render(){return this.tabs?N`
            <sl-tab-group>
                ${this.tabs.map((t=>N`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
      `:N``}}customElements.define("tab-group",si);class ii extends et{static properties={src:{type:String},reportInfo:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};static styles=r`
        .report-head {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .report-title {
            font-family: Arial, sans-serif;
        }
    `;async connectedCallback(){super.connectedCallback();try{const t=await fetch(this.src);this.reportInfo=await t.json(),this.toolname=this.reportInfo.toolname,this.titleDescr=this.reportInfo.title_descr,this.tabFile=this.reportInfo.tab_file,this.introtbl=this.reportInfo.intro_tbl}catch(t){t instanceof TypeError&&(this.fetchFailed=!0)}}corsWarning(){return N`
        <sl-alert variant="danger" open>
          Warning: it looks like you might be trying to view this report
          locally.  See our documentation on how to do that <a
          href="https://intel.github.io/wult/pages/howto.html#open-wult-reports-locally">
            here.</a>
          </sl-alert>
      `}render(){return this.fetchFailed?this.corsWarning():N`
            <div class="report-head">
                <h1 class="report-title">${this.toolname} report</h1>
                ${this.titleDescr?N`
                    <p class="title_descr">${this.titleDescr}</p>
                    <br>
                    `:N``}

                <intro-tbl .src=${this.introtbl}></intro-tbl>
            </div>
            <br>
            <tab-group .tabFile="${this.tabFile}"></tab-group>
        `}}customElements.define("report-page",ii),Ge("shoelace")})();