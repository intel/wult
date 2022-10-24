/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window,e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),s=new WeakMap;class o{constructor(t,e,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const i=this.t;if(e&&void 0===t){const e=void 0!==i&&1===i.length;e&&(t=s.get(i)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&s.set(i,t))}return t}toString(){return this.cssText}}const r=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1]),t[0]);return new o(s,t,i)},n=e?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new o("string"==typeof t?t:t+"",void 0,i))(e)})(t):t;var a;const l=window,d=l.trustedTypes,c=d?d.emptyScript:"",h=l.reactiveElementPolyfillSupport,u={toAttribute(t,e){switch(e){case Boolean:t=t?c:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},p=(t,e)=>e!==t&&(e==e||t==t),b={attribute:!0,type:String,converter:u,reflect:!1,hasChanged:p};class v extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this.u()}static addInitializer(t){var e;null!==(e=this.h)&&void 0!==e||(this.h=[]),this.h.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))})),t}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const o=this[t];this[e]=s,this.requestUpdate(t,o,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||b}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}u(){var t;this._$E_=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])}))}createRenderRoot(){var i;const s=null!==(i=this.shadowRoot)&&void 0!==i?i:this.attachShadow(this.constructor.shadowRootOptions);return((i,s)=>{e?i.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((e=>{const s=document.createElement("style"),o=t.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=e.cssText,i.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=b){var s;const o=this.constructor._$Ep(t,i);if(void 0!==o&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:u).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(o):this.setAttribute(o,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,o=s._$Ev.get(t);if(void 0!==o&&this._$El!==o){const t=s.getPropertyOptions(o),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:u;this._$El=o,this[o]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach(((t,e)=>this[e]=t)),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$EO(e,this[e],t))),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}}var f;v.finalized=!0,v.elementProperties=new Map,v.elementStyles=[],v.shadowRootOptions={mode:"open"},null==h||h({ReactiveElement:v}),(null!==(a=l.reactiveElementVersions)&&void 0!==a?a:l.reactiveElementVersions=[]).push("1.4.1");const m=window,g=m.trustedTypes,y=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,_=`lit$${(Math.random()+"").slice(9)}$`,w="?"+_,$=`<${w}>`,x=document,k=(t="")=>x.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,C=Array.isArray,E=t=>C(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]),S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,T=/-->/g,z=/>/g,P=RegExp(">|[ \t\n\f\r](?:([^\\s\"'>=/]+)([ \t\n\f\r]*=[ \t\n\f\r]*(?:[^ \t\n\f\r\"'`<>=]|(\"|')|))|$)","g"),L=/'/g,I=/"/g,U=/^(?:script|style|textarea|title)$/i,O=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),D=O(1),H=(O(2),Symbol.for("lit-noChange")),N=Symbol.for("lit-nothing"),F=new WeakMap,M=x.createTreeWalker(x,129,null,!1),R=(t,e)=>{const i=t.length-1,s=[];let o,r=2===e?"<svg>":"",n=S;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(n.lastIndex=c,l=n.exec(i),null!==l);)c=n.lastIndex,n===S?"!--"===l[1]?n=T:void 0!==l[1]?n=z:void 0!==l[2]?(U.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=P):void 0!==l[3]&&(n=P):n===P?">"===l[0]?(n=null!=o?o:S,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?P:'"'===l[3]?I:L):n===I||n===L?n=P:n===T||n===z?n=S:(n=P,o=void 0);const h=n===P&&t[e+1].startsWith("/>")?" ":"";r+=n===S?i+$:d>=0?(s.push(a),i.slice(0,d)+"$lit$"+i.slice(d)+_+h):i+_+(-2===d?(s.push(void 0),e):h)}const a=r+(t[i]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==y?y.createHTML(a):a,s]};class B{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,d]=R(t,e);if(this.el=B.createElement(l,i),M.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=M.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(_)){const i=d[r++];if(t.push(e),void 0!==i){const t=s.getAttribute(i.toLowerCase()+"$lit$").split(_),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?K:"?"===e[1]?X:"@"===e[1]?Z:W})}else a.push({type:6,index:o})}for(const e of t)s.removeAttribute(e)}if(U.test(s.tagName)){const t=s.textContent.split(_),e=t.length-1;if(e>0){s.textContent=g?g.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],k()),M.nextNode(),a.push({type:2,index:++o});s.append(t[e],k())}}}else if(8===s.nodeType)if(s.data===w)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(_,t+1));)a.push({type:7,index:o}),t+=_.length-1}o++}}static createElement(t,e){const i=x.createElement("template");return i.innerHTML=t,i}}function V(t,e,i=t,s){var o,r,n,a;if(e===H)return e;let l=void 0!==s?null===(o=i._$Cl)||void 0===o?void 0:o[s]:i._$Cu;const d=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(n=(a=i)._$Cl)&&void 0!==n?n:a._$Cl=[])[s]=l:i._$Cu=l),void 0!==l&&(e=V(t,l._$AS(t,e.values),l,s)),e}class j{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:i},parts:s}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:x).importNode(i,!0);M.currentNode=o;let r=M.nextNode(),n=0,a=0,l=s[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new q(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new J(r,this,t)),this.v.push(e),l=s[++a]}n!==(null==l?void 0:l.index)&&(r=M.nextNode(),n++)}return o}m(t){let e=0;for(const i of this.v)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class q{constructor(t,e,i,s){var o;this.type=2,this._$AH=N,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$C_=null===(o=null==s?void 0:s.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$C_}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=V(this,t,e),A(t)?t===N||null==t||""===t?(this._$AH!==N&&this._$AR(),this._$AH=N):t!==this._$AH&&t!==H&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):E(t)?this.O(t):this.$(t)}S(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.S(t))}$(t){this._$AH!==N&&A(this._$AH)?this._$AA.nextSibling.data=t:this.k(x.createTextNode(t)),this._$AH=t}T(t){var e;const{values:i,_$litType$:s}=t,o="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=B.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(i);else{const t=new j(o,this),e=t.p(this.options);t.m(i),this.k(e),this._$AH=t}}_$AC(t){let e=F.get(t.strings);return void 0===e&&F.set(t.strings,e=new B(t)),e}O(t){C(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new q(this.S(k()),this.S(k()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$C_=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class W{constructor(t,e,i,s,o){this.type=1,this._$AH=N,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=N}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const o=this.strings;let r=!1;if(void 0===o)t=V(this,t,e,0),r=!A(t)||t!==this._$AH&&t!==H,r&&(this._$AH=t);else{const s=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=V(this,s[i+n],e,n),a===H&&(a=this._$AH[n]),r||(r=!A(a)||a!==this._$AH[n]),a===N?t=N:t!==N&&(t+=(null!=a?a:"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.P(t)}P(t){t===N?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class K extends W{constructor(){super(...arguments),this.type=3}P(t){this.element[this.name]=t===N?void 0:t}}const Y=g?g.emptyScript:"";class X extends W{constructor(){super(...arguments),this.type=4}P(t){t&&t!==N?this.element.setAttribute(this.name,Y):this.element.removeAttribute(this.name)}}class Z extends W{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=V(this,t,e,0))&&void 0!==i?i:N)===H)return;const s=this._$AH,o=t===N&&s!==N||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==N&&(s===N||o);o&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}}class J{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){V(this,t)}}const G={A:"$lit$",M:_,C:w,L:1,R,D:j,V:E,I:V,H:q,N:W,U:X,B:Z,F:K,W:J},Q=m.litHtmlPolyfillSupport;var tt,et;null==Q||Q(B,q),(null!==(f=m.litHtmlVersions)&&void 0!==f?f:m.litHtmlVersions=[]).push("2.3.1");class it extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,o;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let n=r._$litPart$;if(void 0===n){const t=null!==(o=null==i?void 0:i.renderBefore)&&void 0!==o?o:null;r._$litPart$=n=new q(e.insertBefore(k(),t),t,void 0,null!=i?i:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return H}}it.finalized=!0,it._$litElement$=!0,null===(tt=globalThis.litElementHydrateSupport)||void 0===tt||tt.call(globalThis,{LitElement:it});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:it}),(null!==(et=globalThis.litElementVersions)&&void 0!==et?et:globalThis.litElementVersions=[]).push("3.2.2");var ot,rt,nt=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,at=Symbol(),lt=new Map,dt=class{constructor(t,e){if(this._$cssResult$=!0,e!==at)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=lt.get(this.cssText);return nt&&void 0===t&&(lt.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},ct=(t,...e)=>{const i=1===t.length?t[0]:e.reduce(((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1]),t[0]);return new dt(i,at)},ht=nt?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new dt("string"==typeof t?t:t+"",at))(e)})(t):t,ut=window.trustedTypes,pt=ut?ut.emptyScript:"",bt=window.reactiveElementPolyfillSupport,vt={toAttribute(t,e){switch(e){case Boolean:t=t?pt:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},ft=(t,e)=>e!==t&&(e==e||t==t),mt={attribute:!0,type:String,converter:vt,reflect:!1,hasChanged:ft},gt=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,i)=>{const s=this._$Eh(i,e);void 0!==s&&(this._$Eu.set(s,i),t.push(s))})),t}static createProperty(t,e=mt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const o=this[t];this[e]=s,this.requestUpdate(t,o,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||mt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(ht(t))}else void 0!==t&&e.push(ht(t));return e}static _$Eh(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,i;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return i=e,s=this.constructor.elementStyles,nt?i.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const e=document.createElement("style"),s=window.litNonce;void 0!==s&&e.setAttribute("nonce",s),e.textContent=t.cssText,i.appendChild(e)})),e;var i,s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ES(t,e,i=mt){var s,o;const r=this.constructor._$Eh(t,i);if(void 0!==r&&!0===i.reflect){const n=(null!==(o=null===(s=i.converter)||void 0===s?void 0:s.toAttribute)&&void 0!==o?o:vt.toAttribute)(e,i.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var i,s,o;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),a=t.converter,l=null!==(o=null!==(s=null===(i=a)||void 0===i?void 0:i.fromAttribute)&&void 0!==s?s:"function"==typeof a?a:null)&&void 0!==o?o:vt.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||ft)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(i)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}};gt.finalized=!0,gt.elementProperties=new Map,gt.elementStyles=[],gt.shadowRootOptions={mode:"open"},null==bt||bt({ReactiveElement:gt}),(null!==(ot=globalThis.reactiveElementVersions)&&void 0!==ot?ot:globalThis.reactiveElementVersions=[]).push("1.3.2");var yt=globalThis.trustedTypes,_t=yt?yt.createPolicy("lit-html",{createHTML:t=>t}):void 0,wt=`lit$${(Math.random()+"").slice(9)}$`,$t="?"+wt,xt=`<${$t}>`,kt=document,At=(t="")=>kt.createComment(t),Ct=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Et=Array.isArray,St=t=>{var e;return Et(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},Tt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,zt=/-->/g,Pt=/>/g,Lt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,It=/'/g,Ut=/"/g,Ot=/^(?:script|style|textarea|title)$/i,Dt=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),Ht=Dt(1),Nt=Dt(2),Ft=Symbol.for("lit-noChange"),Mt=Symbol.for("lit-nothing"),Rt=new WeakMap,Bt=kt.createTreeWalker(kt,129,null,!1),Vt=(t,e)=>{const i=t.length-1,s=[];let o,r=2===e?"<svg>":"",n=Tt;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(n.lastIndex=c,l=n.exec(i),null!==l);)c=n.lastIndex,n===Tt?"!--"===l[1]?n=zt:void 0!==l[1]?n=Pt:void 0!==l[2]?(Ot.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=Lt):void 0!==l[3]&&(n=Lt):n===Lt?">"===l[0]?(n=null!=o?o:Tt,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Lt:'"'===l[3]?Ut:It):n===Ut||n===It?n=Lt:n===zt||n===Pt?n=Tt:(n=Lt,o=void 0);const h=n===Lt&&t[e+1].startsWith("/>")?" ":"";r+=n===Tt?i+xt:d>=0?(s.push(a),i.slice(0,d)+"$lit$"+i.slice(d)+wt+h):i+wt+(-2===d?(s.push(void 0),e):h)}const a=r+(t[i]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==_t?_t.createHTML(a):a,s]},jt=class{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,d]=Vt(t,e);if(this.el=jt.createElement(l,i),Bt.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=Bt.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(wt)){const i=d[r++];if(t.push(e),void 0!==i){const t=s.getAttribute(i.toLowerCase()+"$lit$").split(wt),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?Jt:"?"===e[1]?Qt:"@"===e[1]?te:Zt})}else a.push({type:6,index:o})}for(const e of t)s.removeAttribute(e)}if(Ot.test(s.tagName)){const t=s.textContent.split(wt),e=t.length-1;if(e>0){s.textContent=yt?yt.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],At()),Bt.nextNode(),a.push({type:2,index:++o});s.append(t[e],At())}}}else if(8===s.nodeType)if(s.data===$t)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(wt,t+1));)a.push({type:7,index:o}),t+=wt.length-1}o++}}static createElement(t,e){const i=kt.createElement("template");return i.innerHTML=t,i}};function qt(t,e,i=t,s){var o,r,n,a;if(e===Ft)return e;let l=void 0!==s?null===(o=i._$Cl)||void 0===o?void 0:o[s]:i._$Cu;const d=Ct(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(n=(a=i)._$Cl)&&void 0!==n?n:a._$Cl=[])[s]=l:i._$Cu=l),void 0!==l&&(e=qt(t,l._$AS(t,e.values),l,s)),e}var Wt,Kt,Yt=class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:i},parts:s}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:kt).importNode(i,!0);Bt.currentNode=o;let r=Bt.nextNode(),n=0,a=0,l=s[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new Xt(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new ee(r,this,t)),this.v.push(e),l=s[++a]}n!==(null==l?void 0:l.index)&&(r=Bt.nextNode(),n++)}return o}m(t){let e=0;for(const i of this.v)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},Xt=class{constructor(t,e,i,s){var o;this.type=2,this._$AH=Mt,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cg=null===(o=null==s?void 0:s.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=qt(this,t,e),Ct(t)?t===Mt||null==t||""===t?(this._$AH!==Mt&&this._$AR(),this._$AH=Mt):t!==this._$AH&&t!==Ft&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):St(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==Mt&&Ct(this._$AH)?this._$AA.nextSibling.data=t:this.k(kt.createTextNode(t)),this._$AH=t}T(t){var e;const{values:i,_$litType$:s}=t,o="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=jt.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(i);else{const t=new Yt(o,this),e=t.p(this.options);t.m(i),this.k(e),this._$AH=t}}_$AC(t){let e=Rt.get(t.strings);return void 0===e&&Rt.set(t.strings,e=new jt(t)),e}S(t){Et(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new Xt(this.M(At()),this.M(At()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Zt=class{constructor(t,e,i,s,o){this.type=1,this._$AH=Mt,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=Mt}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const o=this.strings;let r=!1;if(void 0===o)t=qt(this,t,e,0),r=!Ct(t)||t!==this._$AH&&t!==Ft,r&&(this._$AH=t);else{const s=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=qt(this,s[i+n],e,n),a===Ft&&(a=this._$AH[n]),r||(r=!Ct(a)||a!==this._$AH[n]),a===Mt?t=Mt:t!==Mt&&(t+=(null!=a?a:"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.C(t)}C(t){t===Mt?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Jt=class extends Zt{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===Mt?void 0:t}},Gt=yt?yt.emptyScript:"",Qt=class extends Zt{constructor(){super(...arguments),this.type=4}C(t){t&&t!==Mt?this.element.setAttribute(this.name,Gt):this.element.removeAttribute(this.name)}},te=class extends Zt{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=qt(this,t,e,0))&&void 0!==i?i:Mt)===Ft)return;const s=this._$AH,o=t===Mt&&s!==Mt||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==Mt&&(s===Mt||o);o&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},ee=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){qt(this,t)}},ie={L:"$lit$",P:wt,V:$t,I:1,N:Vt,R:Yt,j:St,D:qt,H:Xt,F:Zt,O:Qt,W:te,B:Jt,Z:ee},se=window.litHtmlPolyfillSupport;null==se||se(jt,Xt),(null!==(rt=globalThis.litHtmlVersions)&&void 0!==rt?rt:globalThis.litHtmlVersions=[]).push("2.2.4");var oe=class extends gt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,i)=>{var s,o;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let n=r._$litPart$;if(void 0===n){const t=null!==(o=null==i?void 0:i.renderBefore)&&void 0!==o?o:null;r._$litPart$=n=new Xt(e.insertBefore(At(),t),t,void 0,null!=i?i:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return Ft}};oe.finalized=!0,oe._$litElement$=!0,null===(Wt=globalThis.litElementHydrateSupport)||void 0===Wt||Wt.call(globalThis,{LitElement:oe});var re=globalThis.litElementPolyfillSupport;null==re||re({LitElement:oe}),(null!==(Kt=globalThis.litElementVersions)&&void 0!==Kt?Kt:globalThis.litElementVersions=[]).push("3.2.0");var ne=ct`
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
`,ae=ct`
  ${ne}

  :host {
    --color: var(--sl-panel-border-color);
    --width: var(--sl-panel-border-width);
    --spacing: var(--sl-spacing-medium);
  }

  :host(:not([vertical])) {
    display: block;
    border-top: solid var(--width) var(--color);
    margin: var(--spacing) 0;
  }

  :host([vertical]) {
    display: inline-block;
    height: 100%;
    border-left: solid var(--width) var(--color);
    margin: 0 var(--spacing);
  }
`,le=(Object.create,Object.defineProperty),de=Object.defineProperties,ce=Object.getOwnPropertyDescriptor,he=Object.getOwnPropertyDescriptors,ue=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),pe=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),be=Object.prototype.propertyIsEnumerable,ve=(t,e,i)=>e in t?le(t,e,{enumerable:!0,configurable:!0,writable:!0,value:i}):t[e]=i,fe=(t,e)=>{for(var i in e||(e={}))pe.call(e,i)&&ve(t,i,e[i]);if(ue)for(var i of ue(e))be.call(e,i)&&ve(t,i,e[i]);return t},me=(t,e)=>de(t,he(e)),ge=(t,e,i,s)=>{for(var o,r=s>1?void 0:s?ce(e,i):e,n=t.length-1;n>=0;n--)(o=t[n])&&(r=(s?o(e,i,r):o(r))||r);return s&&r&&le(e,i,r),r};function ye(t,e){const i=fe({waitUntilFirstUpdate:!1},e);return(e,s)=>{const{update:o}=e;if(t in e){const r=t;e.update=function(t){if(t.has(r)){const e=t.get(r),o=this[r];e!==o&&(i.waitUntilFirstUpdate&&!this.hasUpdated||this[s](e,o))}o.call(this,t)}}}}var _e=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:i,elements:s}=e;return{kind:i,elements:s,finisher(e){window.customElements.define(t,e)}}})(t,e),we=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?me(fe({},e),{finisher(i){i.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function $e(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):we(t,e)}function xe(t){return $e(me(fe({},t),{state:!0}))}var ke;function Ae(t,e){return(({finisher:t,descriptor:e})=>(i,s)=>{var o;if(void 0===s){const s=null!==(o=i.originalKey)&&void 0!==o?o:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:me(fe({},i),{key:s});return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const o=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(o,s)}})({descriptor:i=>{const s={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof i?Symbol():"__"+i;s.get=function(){var i,s;return void 0===this[e]&&(this[e]=null!==(s=null===(i=this.renderRoot)||void 0===i?void 0:i.querySelector(t))&&void 0!==s?s:null),this[e]}}return s}})}null===(ke=window.HTMLSlotElement)||void 0===ke||ke.prototype.assignedElements;var Ce=class extends oe{constructor(){super(...arguments),this.vertical=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","separator")}handleVerticalChange(){this.setAttribute("aria-orientation",this.vertical?"vertical":"horizontal")}};function Ee(t){const e=t.tagName.toLowerCase();return"-1"!==t.getAttribute("tabindex")&&!t.hasAttribute("disabled")&&(!t.hasAttribute("aria-disabled")||"false"===t.getAttribute("aria-disabled"))&&!("input"===e&&"radio"===t.getAttribute("type")&&!t.hasAttribute("checked"))&&null!==t.offsetParent&&"hidden"!==window.getComputedStyle(t).visibility&&(!("audio"!==e&&"video"!==e||!t.hasAttribute("controls"))||!!t.hasAttribute("tabindex")||!(!t.hasAttribute("contenteditable")||"false"===t.getAttribute("contenteditable"))||["button","input","select","textarea","a","audio","video","summary"].includes(e))}Ce.styles=ae,ge([$e({type:Boolean,reflect:!0})],Ce.prototype,"vertical",2),ge([ye("vertical")],Ce.prototype,"handleVerticalChange",1),Ce=ge([_e("sl-divider")],Ce);var Se=[],Te=new Set;function ze(t){Te.add(t),document.body.classList.add("sl-scroll-lock")}function Pe(t){Te.delete(t),0===Te.size&&document.body.classList.remove("sl-scroll-lock")}function Le(t,e,i="vertical",s="smooth"){const o=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=o.top+e.scrollTop,n=o.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,d=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==i&&"both"!==i||(n<a?e.scrollTo({left:n,behavior:s}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:s})),"vertical"!==i&&"both"!==i||(r<d?e.scrollTo({top:r,behavior:s}):r+t.clientHeight>c&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:s}))}var Ie=ct`
  ${ne}

  :host {
    --width: 31rem;
    --header-spacing: var(--sl-spacing-large);
    --body-spacing: var(--sl-spacing-large);
    --footer-spacing: var(--sl-spacing-large);

    display: contents;
  }

  .dialog {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: var(--sl-z-index-dialog);
  }

  .dialog__panel {
    display: flex;
    flex-direction: column;
    z-index: 2;
    width: var(--width);
    max-width: calc(100% - var(--sl-spacing-2x-large));
    max-height: calc(100% - var(--sl-spacing-2x-large));
    background-color: var(--sl-panel-background-color);
    border-radius: var(--sl-border-radius-medium);
    box-shadow: var(--sl-shadow-x-large);
  }

  .dialog__panel:focus {
    outline: none;
  }

  /* Ensure there's enough vertical padding for phones that don't update vh when chrome appears (e.g. iPhone) */
  @media screen and (max-width: 420px) {
    .dialog__panel {
      max-height: 80vh;
    }
  }

  .dialog--open .dialog__panel {
    display: flex;
    opacity: 1;
    transform: none;
  }

  .dialog__header {
    flex: 0 0 auto;
    display: flex;
  }

  .dialog__title {
    flex: 1 1 auto;
    font: inherit;
    font-size: var(--sl-font-size-large);
    line-height: var(--sl-line-height-dense);
    padding: var(--header-spacing);
    margin: 0;
  }

  .dialog__close {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-x-large);
    padding: 0 var(--header-spacing);
  }

  .dialog__body {
    flex: 1 1 auto;
    padding: var(--body-spacing);
    overflow: auto;
    -webkit-overflow-scrolling: touch;
  }

  .dialog__footer {
    flex: 0 0 auto;
    text-align: right;
    padding: var(--footer-spacing);
  }

  .dialog__footer ::slotted(sl-button:not(:first-of-type)) {
    margin-inline-start: var(--sl-spacing-x-small);
  }

  .dialog:not(.dialog--has-footer) .dialog__footer {
    display: none;
  }

  .dialog__overlay {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background-color: var(--sl-overlay-background-color);
  }
`;function Ue(t,e,i){return new Promise((s=>{if((null==i?void 0:i.duration)===1/0)throw new Error("Promise-based animations must be finite.");const o=t.animate(e,me(fe({},i),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:i.duration}));o.addEventListener("cancel",s,{once:!0}),o.addEventListener("finish",s,{once:!0})}))}function Oe(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const i=requestAnimationFrame(e);t.addEventListener("cancel",(()=>i),{once:!0}),t.addEventListener("finish",(()=>i),{once:!0}),t.cancel()})))))}function De(t,e){return t.map((t=>me(fe({},t),{height:"auto"===t.height?`${e}px`:t.height})))}var He=new Map,Ne=new WeakMap;function Fe(t,e){return"rtl"===e.toLowerCase()?{keyframes:t.rtlKeyframes||t.keyframes,options:t.options}:t}function Me(t,e){He.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function Re(t,e,i){const s=Ne.get(t);if(null==s?void 0:s[e])return Fe(s[e],i.dir);const o=He.get(e);return o?Fe(o,i.dir):{keyframes:[],options:{duration:0}}}var Be,Ve=new Set,je=new MutationObserver(Ye),qe=new Map,We=document.documentElement.dir||"ltr",Ke=document.documentElement.lang||navigator.language;function Ye(){We=document.documentElement.dir||"ltr",Ke=document.documentElement.lang||navigator.language,[...Ve.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}je.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]});var Xe=class extends class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Ve.add(this.host)}hostDisconnected(){Ve.delete(this.host)}dir(){return`${this.host.dir||We}`.toLowerCase()}lang(){return`${this.host.lang||Ke}`.toLowerCase()}term(t,...e){const i=this.lang().toLowerCase().slice(0,2),s=this.lang().length>2?this.lang().toLowerCase():"",o=qe.get(s),r=qe.get(i);let n;if(o&&o[t])n=o[t];else if(r&&r[t])n=r[t];else{if(!Be||!Be[t])return console.error(`No translation found for: ${String(t)}`),t;n=Be[t]}return"function"==typeof n?n(...e):n}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,i){return new Intl.RelativeTimeFormat(this.lang(),i).format(t,e)}}{};!function(...t){t.map((t=>{const e=t.$code.toLowerCase();qe.has(e)?qe.set(e,Object.assign(Object.assign({},qe.get(e)),t)):qe.set(e,t),Be||(Be=t)})),Ye()}({$code:"en",$name:"English",$dir:"ltr",clearEntry:"Clear entry",close:"Close",copy:"Copy",currentValue:"Current value",hidePassword:"Hide password",loading:"Loading",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",toggleColorFormat:"Toggle color format"});var Ze=class{constructor(t,...e){this.slotNames=[],(this.host=t).addController(this),this.slotNames=e,this.handleSlotChange=this.handleSlotChange.bind(this)}hasDefaultSlot(){return[...this.host.childNodes].some((t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1}))}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}handleSlotChange(t){const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()}},Je=t=>(...e)=>({_$litDirective$:t,values:e}),Ge=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},Qe=Je(class extends Ge{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.et){this.et=new Set,void 0!==t.strings&&(this.st=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(i=this.st)||void 0===i?void 0:i.has(t))&&this.et.add(t);return this.render(e)}const o=t.element.classList;this.et.forEach((t=>{t in e||(o.remove(t),this.et.delete(t))}));for(const t in e){const i=!!e[t];i===this.et.has(t)||(null===(s=this.st)||void 0===s?void 0:s.has(t))||(i?(o.add(t),this.et.add(t)):(o.remove(t),this.et.delete(t)))}return Ft}}),ti=t=>null!=t?t:Mt;function ei(t,e,i){const s=new CustomEvent(e,fe({bubbles:!0,cancelable:!1,composed:!0,detail:{}},i));return t.dispatchEvent(s),s}function ii(t,e){return new Promise((i=>{t.addEventListener(e,(function s(o){o.target===t&&(t.removeEventListener(e,s),i())}))}))}var si=class extends oe{constructor(){super(...arguments),this.hasSlotController=new Ze(this,"footer"),this.localize=new Xe(this),this.open=!1,this.label="",this.noHeader=!1}connectedCallback(){super.connectedCallback(),this.modal=new class{constructor(t){this.tabDirection="forward",this.element=t,this.handleFocusIn=this.handleFocusIn.bind(this),this.handleKeyDown=this.handleKeyDown.bind(this),this.handleKeyUp=this.handleKeyUp.bind(this)}activate(){Se.push(this.element),document.addEventListener("focusin",this.handleFocusIn),document.addEventListener("keydown",this.handleKeyDown),document.addEventListener("keyup",this.handleKeyUp)}deactivate(){Se=Se.filter((t=>t!==this.element)),document.removeEventListener("focusin",this.handleFocusIn),document.removeEventListener("keydown",this.handleKeyDown),document.removeEventListener("keyup",this.handleKeyUp)}isActive(){return Se[Se.length-1]===this.element}checkFocus(){if(this.isActive()&&!this.element.matches(":focus-within")){const{start:t,end:e}=function(t){var e,i;const s=[];return function t(e){e instanceof HTMLElement&&(s.push(e),null!==e.shadowRoot&&"open"===e.shadowRoot.mode&&t(e.shadowRoot)),[...e.children].forEach((e=>t(e)))}(t),{start:null!=(e=s.find((t=>Ee(t))))?e:null,end:null!=(i=s.reverse().find((t=>Ee(t))))?i:null}}(this.element),i="forward"===this.tabDirection?t:e;"function"==typeof(null==i?void 0:i.focus)&&i.focus({preventScroll:!0})}}handleFocusIn(){this.checkFocus()}handleKeyDown(t){"Tab"===t.key&&t.shiftKey&&(this.tabDirection="backward"),requestAnimationFrame((()=>this.checkFocus()))}handleKeyUp(){this.tabDirection="forward"}}(this)}firstUpdated(){this.dialog.hidden=!this.open,this.open&&(this.modal.activate(),ze(this))}disconnectedCallback(){super.disconnectedCallback(),Pe(this)}async show(){if(!this.open)return this.open=!0,ii(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,ii(this,"sl-after-hide")}requestClose(t){if(ei(this,"sl-request-close",{cancelable:!0,detail:{source:t}}).defaultPrevented){const t=Re(this,"dialog.denyClose",{dir:this.localize.dir()});Ue(this.panel,t.keyframes,t.options)}else this.hide()}handleKeyDown(t){"Escape"===t.key&&(t.stopPropagation(),this.requestClose("keyboard"))}async handleOpenChange(){if(this.open){ei(this,"sl-show"),this.originalTrigger=document.activeElement,this.modal.activate(),ze(this);const t=this.querySelector("[autofocus]");t&&t.removeAttribute("autofocus"),await Promise.all([Oe(this.dialog),Oe(this.overlay)]),this.dialog.hidden=!1,requestAnimationFrame((()=>{ei(this,"sl-initial-focus",{cancelable:!0}).defaultPrevented||(t?t.focus({preventScroll:!0}):this.panel.focus({preventScroll:!0})),t&&t.setAttribute("autofocus","")}));const e=Re(this,"dialog.show",{dir:this.localize.dir()}),i=Re(this,"dialog.overlay.show",{dir:this.localize.dir()});await Promise.all([Ue(this.panel,e.keyframes,e.options),Ue(this.overlay,i.keyframes,i.options)]),ei(this,"sl-after-show")}else{ei(this,"sl-hide"),this.modal.deactivate(),await Promise.all([Oe(this.dialog),Oe(this.overlay)]);const t=Re(this,"dialog.hide",{dir:this.localize.dir()}),e=Re(this,"dialog.overlay.hide",{dir:this.localize.dir()});await Promise.all([Ue(this.panel,t.keyframes,t.options),Ue(this.overlay,e.keyframes,e.options)]),this.dialog.hidden=!0,Pe(this);const i=this.originalTrigger;"function"==typeof(null==i?void 0:i.focus)&&setTimeout((()=>i.focus())),ei(this,"sl-after-hide")}}render(){return Ht`
      <div
        part="base"
        class=${Qe({dialog:!0,"dialog--open":this.open,"dialog--has-footer":this.hasSlotController.test("footer")})}
        @keydown=${this.handleKeyDown}
      >
        <div part="overlay" class="dialog__overlay" @click=${()=>this.requestClose("overlay")} tabindex="-1"></div>

        <div
          part="panel"
          class="dialog__panel"
          role="dialog"
          aria-modal="true"
          aria-hidden=${this.open?"false":"true"}
          aria-label=${ti(this.noHeader?this.label:void 0)}
          aria-labelledby=${ti(this.noHeader?void 0:"title")}
          tabindex="0"
        >
          ${this.noHeader?"":Ht`
                <header part="header" class="dialog__header">
                  <h2 part="title" class="dialog__title" id="title">
                    <slot name="label"> ${this.label.length>0?this.label:String.fromCharCode(65279)} </slot>
                  </h2>
                  <sl-icon-button
                    part="close-button"
                    exportparts="base:close-button__base"
                    class="dialog__close"
                    name="x"
                    label=${this.localize.term("close")}
                    library="system"
                    @click="${()=>this.requestClose("close-button")}"
                  ></sl-icon-button>
                </header>
              `}

          <div part="body" class="dialog__body">
            <slot></slot>
          </div>

          <footer part="footer" class="dialog__footer">
            <slot name="footer"></slot>
          </footer>
        </div>
      </div>
    `}};si.styles=Ie,ge([Ae(".dialog")],si.prototype,"dialog",2),ge([Ae(".dialog__panel")],si.prototype,"panel",2),ge([Ae(".dialog__overlay")],si.prototype,"overlay",2),ge([$e({type:Boolean,reflect:!0})],si.prototype,"open",2),ge([$e({reflect:!0})],si.prototype,"label",2),ge([$e({attribute:"no-header",type:Boolean,reflect:!0})],si.prototype,"noHeader",2),ge([ye("open",{waitUntilFirstUpdate:!0})],si.prototype,"handleOpenChange",1),si=ge([_e("sl-dialog")],si),Me("dialog.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),Me("dialog.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}}),Me("dialog.denyClose",{keyframes:[{transform:"scale(1)"},{transform:"scale(1.02)"},{transform:"scale(1)"}],options:{duration:250}}),Me("dialog.overlay.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:250}}),Me("dialog.overlay.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:250}});var oi=ct`
  ${ne}

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

  .icon-button:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  .icon-button__icon {
    pointer-events: none;
  }
`,ri=Symbol.for(""),ni=t=>{var e,i;if((null===(e=t)||void 0===e?void 0:e.r)===ri)return null===(i=t)||void 0===i?void 0:i._$litStatic$},ai=(t,...e)=>({_$litStatic$:e.reduce(((e,i,s)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(i)+t[s+1]),t[0]),r:ri}),li=new Map,di=t=>(e,...i)=>{const s=i.length;let o,r;const n=[],a=[];let l,d=0,c=!1;for(;d<s;){for(l=e[d];d<s&&void 0!==(r=i[d],o=ni(r));)l+=o+e[++d],c=!0;a.push(r),n.push(l),d++}if(d===s&&n.push(e[s]),c){const t=n.join("$$lit$$");void 0===(e=li.get(t))&&(n.raw=n,li.set(t,e=n)),i=a}return t(e,...i)},ci=di(Ht),hi=(di(Nt),class extends oe{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,ei(this,"sl-blur")}handleFocus(){this.hasFocus=!0,ei(this,"sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}render(){const t=!!this.href,e=t?ai`a`:ai`button`;return ci`
      <${e}
        part="base"
        class=${Qe({"icon-button":!0,"icon-button--disabled":!t&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${ti(t?void 0:this.disabled)}
        type=${ti(t?void 0:"button")}
        href=${ti(t?this.href:void 0)}
        target=${ti(t?this.target:void 0)}
        download=${ti(t?this.download:void 0)}
        rel=${ti(t&&this.target?"noreferrer noopener":void 0)}
        role=${ti(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          class="icon-button__icon"
          name=${ti(this.name)}
          library=${ti(this.library)}
          src=${ti(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${e}>
    `}});hi.styles=oi,ge([xe()],hi.prototype,"hasFocus",2),ge([Ae(".icon-button")],hi.prototype,"button",2),ge([$e()],hi.prototype,"name",2),ge([$e()],hi.prototype,"library",2),ge([$e()],hi.prototype,"src",2),ge([$e()],hi.prototype,"href",2),ge([$e()],hi.prototype,"target",2),ge([$e()],hi.prototype,"download",2),ge([$e()],hi.prototype,"label",2),ge([$e({type:Boolean,reflect:!0})],hi.prototype,"disabled",2),hi=ge([_e("sl-icon-button")],hi);var ui="";function pi(t){ui=t}var bi={name:"default",resolver:t=>`${function(){if(!ui){const t=[...document.getElementsByTagName("script")],e=t.find((t=>t.hasAttribute("data-shoelace")));if(e)pi(e.getAttribute("data-shoelace"));else{const e=t.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let i="";e&&(i=e.getAttribute("src")),pi(i.split("/").slice(0,-1).join("/"))}}return ui.replace(/\/$/,"")}()}/assets/icons/${t}.svg`},vi={"check-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">\n      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"></path>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},fi=[bi,{name:"system",resolver:t=>t in vi?`data:image/svg+xml,${encodeURIComponent(vi[t])}`:""}],mi=[];function gi(t){return fi.find((e=>e.name===t))}var yi=new Map,_i=new Map;var wi=ct`
  ${ne}

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
`,$i=class extends Ge{constructor(t){if(super(t),this.it=Mt,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===Mt||null==t)return this.ft=void 0,this.it=t;if(t===Ft)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.ft;this.it=t;const e=[t];return e.raw=e,this.ft={_$litType$:this.constructor.resultType,strings:e,values:[]}}};$i.directiveName="unsafeHTML",$i.resultType=1,Je($i);var xi=class extends $i{};xi.directiveName="unsafeSVG",xi.resultType=2;var ki,Ai=Je(xi),Ci=class extends oe{constructor(){super(...arguments),this.svg="",this.label="",this.library="default"}connectedCallback(){super.connectedCallback(),mi.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,mi=mi.filter((e=>e!==t))}getUrl(){const t=gi(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){var t;const e=gi(this.library),i=this.getUrl();if(ki||(ki=new DOMParser),i)try{const s=await async function(t){if(_i.has(t))return _i.get(t);const e=await function(t,e="cors"){if(yi.has(t))return yi.get(t);const i=fetch(t,{mode:e}).then((async t=>({ok:t.ok,status:t.status,html:await t.text()})));return yi.set(t,i),i}(t),i={ok:e.ok,status:e.status,svg:null};if(e.ok){const t=document.createElement("div");t.innerHTML=e.html;const s=t.firstElementChild;i.svg="svg"===(null==s?void 0:s.tagName.toLowerCase())?s.outerHTML:""}return _i.set(t,i),i}(i);if(i!==this.getUrl())return;if(s.ok){const i=ki.parseFromString(s.svg,"text/html").body.querySelector("svg");null!==i?(null==(t=null==e?void 0:e.mutator)||t.call(e,i),this.svg=i.outerHTML,ei(this,"sl-load")):(this.svg="",ei(this,"sl-error"))}else this.svg="",ei(this,"sl-error")}catch(t){ei(this,"sl-error")}else this.svg.length>0&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return Ht` <div
      part="base"
      class="icon"
      role=${ti(t?"img":void 0)}
      aria-label=${ti(t?this.label:void 0)}
      aria-hidden=${ti(t?void 0:"true")}
    >
      ${Ai(this.svg)}
    </div>`}};Ci.styles=wi,ge([xe()],Ci.prototype,"svg",2),ge([$e({reflect:!0})],Ci.prototype,"name",2),ge([$e()],Ci.prototype,"src",2),ge([$e()],Ci.prototype,"label",2),ge([$e({reflect:!0})],Ci.prototype,"library",2),ge([ye("name"),ye("src"),ye("library")],Ci.prototype,"setIcon",1),Ci=ge([_e("sl-icon")],Ci);const{H:Ei}=G,Si=t=>(...e)=>({_$litDirective$:t,values:e}),Ti=(t,e)=>{var i,s;const o=t._$AN;if(void 0===o)return!1;for(const t of o)null===(s=(i=t)._$AO)||void 0===s||s.call(i,e,!1),Ti(t,e);return!0},zi=t=>{let e,i;do{if(void 0===(e=t._$AM))break;i=e._$AN,i.delete(t),t=e}while(0===(null==i?void 0:i.size))},Pi=t=>{for(let e;e=t._$AM;t=e){let i=e._$AN;if(void 0===i)e._$AN=i=new Set;else if(i.has(t))break;i.add(t),Ui(e)}};function Li(t){void 0!==this._$AN?(zi(this),this._$AM=t,Pi(this)):this._$AM=t}function Ii(t,e=!1,i=0){const s=this._$AH,o=this._$AN;if(void 0!==o&&0!==o.size)if(e)if(Array.isArray(s))for(let t=i;t<s.length;t++)Ti(s[t],!1),zi(s[t]);else null!=s&&(Ti(s,!1),zi(s));else Ti(this,t)}const Ui=t=>{var e,i,s,o;2==t.type&&(null!==(e=(s=t)._$AP)&&void 0!==e||(s._$AP=Ii),null!==(i=(o=t)._$AQ)&&void 0!==i||(o._$AQ=Li))};class Oi extends class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,i){super._$AT(t,e,i),Pi(this),this.isConnected=t._$AU}_$AO(t,e=!0){var i,s;t!==this.isConnected&&(this.isConnected=t,t?null===(i=this.reconnected)||void 0===i||i.call(this):null===(s=this.disconnected)||void 0===s||s.call(this)),e&&(Ti(this,t),zi(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Di{constructor(t){this.Y=t}disconnect(){this.Y=void 0}reconnect(t){this.Y=t}deref(){return this.Y}}class Hi{constructor(){this.Z=void 0,this.q=void 0}get(){return this.Z}pause(){var t;null!==(t=this.Z)&&void 0!==t||(this.Z=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Z=this.q=void 0}}const Ni=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,Fi=Si(class extends Oi{constructor(){super(...arguments),this._$Cwt=1073741823,this._$Cyt=[],this._$CK=new Di(this),this._$CX=new Hi}render(...t){var e;return null!==(e=t.find((t=>!Ni(t))))&&void 0!==e?e:H}update(t,e){const i=this._$Cyt;let s=i.length;this._$Cyt=e;const o=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cwt);t++){const n=e[t];if(!Ni(n))return this._$Cwt=t,n;t<s&&n===i[t]||(this._$Cwt=1073741823,s=0,Promise.resolve(n).then((async t=>{for(;r.get();)await r.get();const e=o.deref();if(void 0!==e){const i=e._$Cyt.indexOf(n);i>-1&&i<e._$Cwt&&(e._$Cwt=i,e.setValue(t))}})))}return H}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}});class Mi{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class Ri extends it{static properties={file:{type:File},template:{attribute:!1}};static styles=r`
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
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),i=t.stream().getReader();let{value:s,done:o}=await i.read();s=s?e.decode(s,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(s);if(t)yield s.substring(n,t.index),n=r.lastIndex;else{if(o)break;const t=s.substr(n);({value:s,done:o}=await i.read()),s=t+(s?e.decode(s,{stream:!0}):""),n=r.lastIndex=0}}n<s.length&&(yield s.substr(n))}render(){if(!this.file)return D``;const t=this.parseSrc();return D`${Fi(t,D``)}`}}customElements.define("sc-report-table",Ri),customElements.define("sc-intro-tbl",class extends Ri{parseHeader(t){const e=t.split(";");return D`
            <tr>
                ${e.map((t=>D`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=D``,i=!0;for(const s of t.split(";")){const[t,o,r]=s.split("|");let n=D`${t}`;r&&(n=D`<a href=${r}>${n}</a>`),o&&(n=D`<abbr title=${o}>${n}</abbr>`),i?(e=D`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,i=!1):e=D`${e}
                    <td>
                        ${n}
                    </td>
                `}return D`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.file);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Mi("first line in intro table file should be a header.");e=e.slice(2);let i=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Mi("lines following the first should all be normal table rows.");e=e.slice(2),i=D`${i}${this.parseRow(e)}`}return D`<table>${i}</table>`}});var Bi=ct`
  ${ne}

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
    padding-inline-start: var(--sl-spacing-large);
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
    padding-inline-end: var(--sl-spacing-medium);
  }
`,Vi=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),ji=class extends oe{constructor(){super(...arguments),this.hasSlotController=new Ze(this,"icon","suffix"),this.localize=new Xe(this),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,ii(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,ii(this,"sl-after-hide")}async toast(){return new Promise((t=>{null===Vi.parentElement&&document.body.append(Vi),Vi.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{Vi.removeChild(this),t(),null===Vi.querySelector("sl-alert")&&Vi.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){ei(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await Oe(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=Re(this,"alert.show",{dir:this.localize.dir()});await Ue(this.base,t,e),ei(this,"sl-after-show")}else{ei(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await Oe(this.base);const{keyframes:t,options:e}=Re(this,"alert.hide",{dir:this.localize.dir()});await Ue(this.base,t,e),this.base.hidden=!0,ei(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return Ht`
      <div
        part="base"
        class=${Qe({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--has-icon":this.hasSlotController.test("icon"),"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
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

        ${this.closable?Ht`
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
    `}};ji.styles=Bi,ge([Ae('[part="base"]')],ji.prototype,"base",2),ge([$e({type:Boolean,reflect:!0})],ji.prototype,"open",2),ge([$e({type:Boolean,reflect:!0})],ji.prototype,"closable",2),ge([$e({reflect:!0})],ji.prototype,"variant",2),ge([$e({type:Number})],ji.prototype,"duration",2),ge([ye("open",{waitUntilFirstUpdate:!0})],ji.prototype,"handleOpenChange",1),ge([ye("duration")],ji.prototype,"handleDurationChange",1),ji=ge([_e("sl-alert")],ji),Me("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),Me("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var qi=ct`
  ${ne}

  :host {
    --indicator-color: var(--sl-color-primary-600);
    --track-color: var(--sl-color-neutral-200);
    --track-width: 2px;

    display: block;
  }

  .tab-group {
    display: flex;
    border: solid 1px transparent;
    border-radius: 0;
  }

  .tab-group__tabs {
    display: flex;
    position: relative;
  }

  .tab-group__indicator {
    position: absolute;
    transition: var(--sl-transition-fast) transform ease, var(--sl-transition-fast) width ease;
  }

  .tab-group--has-scroll-controls .tab-group__nav-container {
    position: relative;
    padding: 0 var(--sl-spacing-x-large);
  }

  .tab-group__body {
    overflow: auto;
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

  .tab-group--rtl .tab-group__scroll-button--start {
    left: auto;
    right: 0;
  }

  .tab-group--rtl .tab-group__scroll-button--end {
    left: 0;
    right: auto;
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
    border-bottom: solid var(--track-width) var(--track-color);
  }

  .tab-group--top .tab-group__indicator {
    bottom: calc(-1 * var(--track-width));
    border-bottom: solid var(--track-width) var(--indicator-color);
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
    border-top: solid var(--track-width) var(--track-color);
  }

  .tab-group--bottom .tab-group__indicator {
    top: calc(-1 * var(--track-width));
    border-top: solid var(--track-width) var(--indicator-color);
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
    border-inline-end: solid var(--track-width) var(--track-color);
  }

  .tab-group--start .tab-group__indicator {
    right: calc(-1 * var(--track-width));
    border-right: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--start.tab-group--rtl .tab-group__indicator {
    right: auto;
    left: calc(-1 * var(--track-width));
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
    border-left: solid var(--track-width) var(--track-color);
  }

  .tab-group--end .tab-group__indicator {
    left: calc(-1 * var(--track-width));
    border-inline-start: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--end.tab-group--rtl .tab-group__indicator {
    right: calc(-1 * var(--track-width));
    left: auto;
  }

  .tab-group--end .tab-group__body {
    flex: 1 1 auto;
    order: 1;
  }

  .tab-group--end ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }
`,Wi=class extends oe{constructor(){super(...arguments),this.localize=new Xe(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{var i;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(i=this.getActiveTab())?i:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t={includeDisabled:!0}){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t.includeDisabled?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement,i="rtl"===this.localize.dir();if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&t.key===(i?"ArrowRight":"ArrowLeft")||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s--:(["top","bottom"].includes(this.placement)&&t.key===(i?"ArrowLeft":"ArrowRight")||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&s++,s<0&&(s=this.tabs.length-1),s>this.tabs.length-1&&(s=0),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Le(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft+this.nav.clientWidth:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft-this.nav.clientWidth:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth}setActiveTab(t,e){if(e=fe({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const i=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)})),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Le(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(i&&ei(this,"sl-tab-hide",{detail:{name:i.panel}}),ei(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,i=t.clientHeight,s="rtl"===this.localize.dir(),o=this.getAllTabs(),r=o.slice(0,o.indexOf(t)).reduce(((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight})),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=s?`translateX(${-1*r.left}px)`:`translateX(${r.left}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${i}px`,this.indicator.style.transform=`translateY(${r.top}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs({includeDisabled:!1}),this.panels=this.getAllPanels(),this.syncIndicator()}render(){const t="rtl"===this.localize.dir();return Ht`
      <div
        part="base"
        class=${Qe({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--rtl":"rtl"===this.localize.dir(),"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?Ht`
                <sl-icon-button
                  part="scroll-button scroll-button--start"
                  exportparts="base:scroll-button__base"
                  class="tab-group__scroll-button tab-group__scroll-button--start"
                  name=${t?"chevron-right":"chevron-left"}
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

          ${this.hasScrollControls?Ht`
                <sl-icon-button
                  part="scroll-button scroll-button--end"
                  exportparts="base:scroll-button__base"
                  class="tab-group__scroll-button tab-group__scroll-button--end"
                  name=${t?"chevron-left":"chevron-right"}
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
    `}};Wi.styles=qi,ge([Ae(".tab-group")],Wi.prototype,"tabGroup",2),ge([Ae(".tab-group__body")],Wi.prototype,"body",2),ge([Ae(".tab-group__nav")],Wi.prototype,"nav",2),ge([Ae(".tab-group__indicator")],Wi.prototype,"indicator",2),ge([xe()],Wi.prototype,"hasScrollControls",2),ge([$e()],Wi.prototype,"placement",2),ge([$e()],Wi.prototype,"activation",2),ge([$e({attribute:"no-scroll-controls",type:Boolean})],Wi.prototype,"noScrollControls",2),ge([$e()],Wi.prototype,"lang",2),ge([ye("noScrollControls",{waitUntilFirstUpdate:!0})],Wi.prototype,"updateScrollControls",1),ge([ye("placement",{waitUntilFirstUpdate:!0})],Wi.prototype,"syncIndicator",1),Wi=ge([_e("sl-tab-group")],Wi);var Ki=0;function Yi(){return++Ki}var Xi=ct`
  ${ne}

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

  .tab:focus-visible:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: calc(-1 * var(--sl-focus-ring-width) - var(--sl-focus-ring-offset));
  }

  .tab.tab--active:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab.tab--closable {
    padding-inline-end: var(--sl-spacing-small);
  }

  .tab.tab--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tab__close-button {
    font-size: var(--sl-font-size-large);
    margin-inline-start: var(--sl-spacing-2x-small);
  }

  .tab__close-button::part(base) {
    padding: var(--sl-spacing-3x-small);
  }
`,Zi=class extends oe{constructor(){super(...arguments),this.localize=new Xe(this),this.attrId=Yi(),this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","tab")}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){ei(this,"sl-close")}handleActiveChange(){this.setAttribute("aria-selected",this.active?"true":"false")}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false")}render(){return this.id=this.id.length>0?this.id:this.componentId,Ht`
      <div
        part="base"
        class=${Qe({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        tabindex="0"
      >
        <slot></slot>
        ${this.closable?Ht`
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
    `}};Zi.styles=Xi,ge([Ae(".tab")],Zi.prototype,"tab",2),ge([$e({reflect:!0})],Zi.prototype,"panel",2),ge([$e({type:Boolean,reflect:!0})],Zi.prototype,"active",2),ge([$e({type:Boolean})],Zi.prototype,"closable",2),ge([$e({type:Boolean,reflect:!0})],Zi.prototype,"disabled",2),ge([$e()],Zi.prototype,"lang",2),ge([ye("active")],Zi.prototype,"handleActiveChange",1),ge([ye("disabled")],Zi.prototype,"handleDisabledChange",1),Zi=ge([_e("sl-tab")],Zi);var Ji=ct`
  ${ne}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }

  .tab-panel:not(.tab-panel--active) {
    display: none;
  }
`,Gi=class extends oe{constructor(){super(...arguments),this.attrId=Yi(),this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId,this.setAttribute("role","tabpanel")}handleActiveChange(){this.setAttribute("aria-hidden",this.active?"false":"true")}render(){return Ht`
      <div
        part="base"
        class=${Qe({"tab-panel":!0,"tab-panel--active":this.active})}
      >
        <slot></slot>
      </div>
    `}};Gi.styles=Ji,ge([$e({reflect:!0})],Gi.prototype,"name",2),ge([$e({type:Boolean,reflect:!0})],Gi.prototype,"active",2),ge([ye("active")],Gi.prototype,"handleActiveChange",1),Gi=ge([_e("sl-tab-panel")],Gi);var Qi=ct`
  ${ne}

  :host {
    /*
     * These are actually used by tree item, but we define them here so they can more easily be set and all tree items
     * stay consistent.
     */
    --indent-guide-color: var(--sl-color-neutral-200);
    --indent-guide-offset: 0;
    --indent-guide-style: solid;
    --indent-guide-width: 0;
    --indent-size: var(--sl-spacing-large);

    display: block;
    isolation: isolate;

    /*
     * Tree item indentation uses the "em" unit to increment its width on each level, so setting the font size to zero
     * here removes the indentation for all the nodes on the first level.
     */
    font-size: 0;
  }
`,ts=ct`
  ${ne}

  :host {
    display: block;
    outline: 0;
    z-index: 0;
  }

  :host(:focus) {
    outline: 0;
  }

  slot:not([name])::slotted(sl-icon) {
    margin-inline-end: var(--sl-spacing-x-small);
  }

  .tree-item {
    position: relative;
    display: flex;
    align-items: stretch;
    flex-direction: column;
    color: var(--sl-color-neutral-700);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }

  .tree-item__checkbox {
    pointer-events: none;
  }

  .tree-item__expand-button,
  .tree-item__checkbox,
  .tree-item__label {
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-medium);
    font-weight: var(--sl-font-weight-normal);
    line-height: var(--sl-line-height-normal);
    letter-spacing: var(--sl-letter-spacing-normal);
  }

  .tree-item__checkbox::part(base) {
    display: flex;
    align-items: center;
  }

  .tree-item__indentation {
    display: block;
    width: 1em;
    flex-shrink: 0;
  }

  .tree-item__expand-button {
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: content-box;
    color: var(--sl-color-neutral-500);
    padding: var(--sl-spacing-x-small);
    width: 1rem;
    height: 1rem;
    cursor: pointer;
  }

  .tree-item__expand-button--visible {
    cursor: pointer;
  }

  .tree-item__item {
    display: flex;
    align-items: center;
    border-inline-start: solid 3px transparent;
  }

  .tree-item--disabled .tree-item__item {
    opacity: 0.5;
    outline: none;
    cursor: not-allowed;
  }

  :host(:focus-visible) .tree-item__item {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
    z-index: 2;
  }

  :host(:not([aria-disabled='true'])) .tree-item--selected .tree-item__item {
    background-color: var(--sl-color-neutral-100);
    border-inline-start-color: var(--sl-color-primary-600);
  }

  :host(:not([aria-disabled='true'])) .tree-item__expand-button {
    color: var(--sl-color-neutral-600);
  }

  .tree-item__label {
    display: flex;
    align-items: center;
    transition: var(--sl-transition-fast) color;
  }

  .tree-item__children {
    font-size: calc(1em + var(--indent-size, var(--sl-spacing-medium)));
  }

  /* Indentation lines */
  .tree-item__children {
    position: relative;
  }

  .tree-item__children::before {
    content: '';
    position: absolute;
    top: var(--indent-guide-offset);
    bottom: var(--indent-guide-offset);
    left: calc(1em - (var(--indent-guide-width) / 2) - 1px);
    border-inline-end: var(--indent-guide-width) var(--indent-guide-style) var(--indent-guide-color);
    z-index: 1;
  }

  .tree-item--rtl .tree-item__children::before {
    left: auto;
    right: 1em;
  }
`,{H:es}=ie,is={},ss=Je(class extends Ge{constructor(t){if(super(t),3!==t.type&&1!==t.type&&4!==t.type)throw Error("The `live` directive is not allowed on child or event bindings");if(!(t=>void 0===t.strings)(t))throw Error("`live` bindings can only contain a single expression")}render(t){return t}update(t,[e]){if(e===Ft||e===Mt)return e;const i=t.element,s=t.name;if(3===t.type){if(e===i[s])return Ft}else if(4===t.type){if(!!e===i.hasAttribute(s))return Ft}else if(1===t.type&&i.getAttribute(s)===e+"")return Ft;return((t,e=is)=>{t._$AH=e})(t),e}});function os(t,e,i){return t?e():null==i?void 0:i()}function rs(t){return t&&"treeitem"===t.getAttribute("role")}var ns=class extends oe{constructor(){super(...arguments),this.localize=new Xe(this),this.indeterminate=!1,this.isLeaf=!1,this.loading=!1,this.selectable=!1,this.expanded=!1,this.selected=!1,this.disabled=!1,this.lazy=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","treeitem"),this.setAttribute("tabindex","-1"),this.isNestedItem()&&(this.slot="children")}firstUpdated(){this.childrenContainer.hidden=!this.expanded,this.childrenContainer.style.height=this.expanded?"auto":"0",this.isLeaf=0===this.getChildrenItems().length,this.handleExpandedChange()}handleLoadingChange(){this.setAttribute("aria-busy",this.loading?"true":"false"),this.loading||this.animateExpand()}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false")}handleSelectedChange(){this.setAttribute("aria-selected",this.selected?"true":"false")}handleExpandedChange(){this.isLeaf?this.removeAttribute("aria-expanded"):this.setAttribute("aria-expanded",this.expanded?"true":"false")}handleExpandAnimation(){this.expanded?this.lazy?(this.loading=!0,ei(this,"sl-lazy-load")):this.animateExpand():this.animateCollapse()}async animateExpand(){ei(this,"sl-expand"),await Oe(this.childrenContainer),this.childrenContainer.hidden=!1;const{keyframes:t,options:e}=Re(this,"tree-item.expand",{dir:this.localize.dir()});await Ue(this.childrenContainer,De(t,this.childrenContainer.scrollHeight),e),this.childrenContainer.style.height="auto",ei(this,"sl-after-expand")}async animateCollapse(){ei(this,"sl-collapse"),await Oe(this.childrenContainer);const{keyframes:t,options:e}=Re(this,"tree-item.collapse",{dir:this.localize.dir()});await Ue(this.childrenContainer,De(t,this.childrenContainer.scrollHeight),e),this.childrenContainer.hidden=!0,ei(this,"sl-after-collapse")}getChildrenItems({includeDisabled:t=!0}={}){return this.childrenSlot?[...this.childrenSlot.assignedElements({flatten:!0})].filter((e=>rs(e)&&(t||!e.disabled))):[]}isNestedItem(){const t=this.parentElement;return!!t&&rs(t)}handleToggleExpand(t){t.preventDefault(),t.stopImmediatePropagation(),this.disabled||(this.expanded=!this.expanded)}handleChildrenSlotChange(){this.loading=!1,this.isLeaf=0===this.getChildrenItems().length}willUpdate(t){t.has("selected")&&!t.has("indeterminate")&&(this.indeterminate=!1)}render(){const t="rtl"===this.localize.dir(),e=!this.loading&&(!this.isLeaf||this.lazy);return Ht`
      <div
        part="base"
        class="${Qe({"tree-item":!0,"tree-item--selected":this.selected,"tree-item--disabled":this.disabled,"tree-item--leaf":this.isLeaf,"tree-item--rtl":"rtl"===this.localize.dir()})}"
      >
        <div
          class="tree-item__item"
          part="
            item
            ${this.disabled?"item--disabled":""}
            ${this.expanded?"item--expanded":""}
            ${this.indeterminate?"item--indeterminate":""}
            ${this.selected?"item--selected":""}
          "
        >
          <div class="tree-item__indentation" part="indentation"></div>

          <div
            class=${Qe({"tree-item__expand-button":!0,"tree-item__expand-button--visible":e})}
            aria-hidden="true"
            @click="${this.handleToggleExpand}"
          >
            ${os(this.loading,(()=>Ht` <sl-spinner></sl-spinner> `))}
            ${os(e,(()=>Ht`
                <slot name="${this.expanded?"expanded-icon":"collapsed-icon"}">
                  <sl-icon
                    library="system"
                    name="${this.expanded?"chevron-down":t?"chevron-left":"chevron-right"}"
                  ></sl-icon>
                </slot>
              `))}
          </div>

          ${os(this.selectable,(()=>Ht`
                <sl-checkbox
                  tabindex="-1"
                  class="tree-item__checkbox"
                  ?disabled="${this.disabled}"
                  ?checked="${ss(this.selected)}"
                  ?indeterminate="${this.indeterminate}"
                >
                  <div class="tree-item__label" part="label">
                    <slot></slot>
                  </div>
                </sl-checkbox>
              `),(()=>Ht`
              <div class="tree-item__label" part="label">
                <slot></slot>
              </div>
            `))}
        </div>

        <div class="tree-item__children" part="children" role="group">
          <slot name="children" @slotchange="${this.handleChildrenSlotChange}"></slot>
        </div>
      </div>
    `}};function as(t,e,i){return t<e?e:t>i?i:t}ns.styles=ts,ge([xe()],ns.prototype,"indeterminate",2),ge([xe()],ns.prototype,"isLeaf",2),ge([xe()],ns.prototype,"loading",2),ge([xe()],ns.prototype,"selectable",2),ge([$e({type:Boolean,reflect:!0})],ns.prototype,"expanded",2),ge([$e({type:Boolean,reflect:!0})],ns.prototype,"selected",2),ge([$e({type:Boolean,reflect:!0})],ns.prototype,"disabled",2),ge([$e({type:Boolean,reflect:!0})],ns.prototype,"lazy",2),ge([Ae("slot:not([name])")],ns.prototype,"defaultSlot",2),ge([Ae("slot[name=children]")],ns.prototype,"childrenSlot",2),ge([Ae(".tree-item__item")],ns.prototype,"itemElement",2),ge([Ae(".tree-item__children")],ns.prototype,"childrenContainer",2),ge([ye("loading",{waitUntilFirstUpdate:!0})],ns.prototype,"handleLoadingChange",1),ge([ye("disabled")],ns.prototype,"handleDisabledChange",1),ge([ye("selected")],ns.prototype,"handleSelectedChange",1),ge([ye("expanded",{waitUntilFirstUpdate:!0})],ns.prototype,"handleExpandedChange",1),ge([ye("expanded",{waitUntilFirstUpdate:!0})],ns.prototype,"handleExpandAnimation",1),ns=ge([_e("sl-tree-item")],ns),Me("tree-item.expand",{keyframes:[{height:"0",opacity:"0",overflow:"hidden"},{height:"auto",opacity:"1",overflow:"hidden"}],options:{duration:250,easing:"cubic-bezier(0.4, 0.0, 0.2, 1)"}}),Me("tree-item.collapse",{keyframes:[{height:"auto",opacity:"1",overflow:"hidden"},{height:"0",opacity:"0",overflow:"hidden"}],options:{duration:200,easing:"cubic-bezier(0.4, 0.0, 0.2, 1)"}});var ls=class extends oe{constructor(){super(...arguments),this.selection="single",this.treeItems=this.getElementsByTagName("sl-tree-item"),this.localize=new Xe(this),this.initTreeItem=t=>{t.selectable="multiple"===this.selection,["expanded","collapsed"].filter((t=>!!this.querySelector(`[slot="${t}-icon"]`))).forEach((e=>{const i=t.querySelector(`[slot="${e}-icon"]`);null===i?t.append(this.getExpandButtonIcon(e)):i.hasAttribute("data-default")&&i.replaceWith(this.getExpandButtonIcon(e))}))},this.handleTreeChanged=t=>{for(const e of t){const t=[...e.addedNodes].filter(rs),i=[...e.removedNodes].filter(rs);t.forEach(this.initTreeItem),i.includes(this.lastFocusedItem)&&this.focusItem(this.getFocusableItems()[0])}},this.handleFocusOut=t=>{const e=t.relatedTarget;e&&this.contains(e)||(this.tabIndex=0)},this.handleFocusIn=t=>{const e=t.target;t.target===this&&this.focusItem(this.lastFocusedItem||this.treeItems[0]),rs(e)&&!e.disabled&&(this.lastFocusedItem&&(this.lastFocusedItem.tabIndex=-1),this.lastFocusedItem=e,this.tabIndex=-1,e.tabIndex=0)}}connectedCallback(){super.connectedCallback(),this.setAttribute("role","tree"),this.setAttribute("tabindex","0"),this.mutationObserver=new MutationObserver(this.handleTreeChanged),this.addEventListener("focusin",this.handleFocusIn),this.addEventListener("focusout",this.handleFocusOut)}disconnectedCallback(){super.disconnectedCallback(),this.mutationObserver.disconnect(),this.removeEventListener("focusin",this.handleFocusIn),this.removeEventListener("focusout",this.handleFocusOut)}getExpandButtonIcon(t){const e=("expanded"===t?this.expandedIconSlot:this.collapsedIconSlot).assignedElements({flatten:!0})[0];if(e){const i=e.cloneNode(!0);return[i,...i.querySelectorAll("[id]")].forEach((t=>t.removeAttribute("id"))),i.setAttribute("data-default",""),i.slot=`${t}-icon`,i}return null}firstUpdated(){[...this.treeItems].forEach(this.initTreeItem),this.mutationObserver.observe(this,{childList:!0,subtree:!0})}handleSelectionChange(){this.setAttribute("aria-multiselectable","multiple"===this.selection?"true":"false");for(const t of this.treeItems)t.selectable="multiple"===this.selection}syncTreeItems(t){if("multiple"===this.selection)(function t(e){const i=e.parentElement;if(rs(i)){const e=i.getChildrenItems({includeDisabled:!1}),s=!!e.length&&e.every((t=>t.selected)),o=e.every((t=>!t.selected&&!t.indeterminate));i.selected=s,i.indeterminate=!s&&!o,t(i)}})(e=t),function t(e){for(const i of e.getChildrenItems())i.selected=!i.disabled&&e.selected,t(i)}(e);else for(const e of this.treeItems)e!==t&&(e.selected=!1);var e}selectItem(t){"multiple"===this.selection?(t.selected=!t.selected,t.lazy&&(t.expanded=!0),this.syncTreeItems(t)):"single"===this.selection||t.isLeaf?(t.selected=!0,this.syncTreeItems(t)):"leaf"===this.selection&&(t.expanded=!t.expanded),ei(this,"sl-selection-change",{detail:{selection:this.selectedItems}})}get selectedItems(){return[...this.treeItems].filter((t=>t.selected))}getFocusableItems(){const t=new Set;return[...this.treeItems].filter((e=>{var i;if(e.disabled)return!1;const s=null==(i=e.parentElement)?void 0:i.closest("[role=treeitem]");return s&&(!s.expanded||s.loading||t.has(s))&&t.add(e),!t.has(e)}))}focusItem(t){null==t||t.focus()}handleKeyDown(t){if(!["ArrowDown","ArrowUp","ArrowRight","ArrowLeft","Home","End","Enter"," "].includes(t.key))return;const e=this.getFocusableItems(),i="ltr"===this.localize.dir(),s="rtl"===this.localize.dir();if(e.length>0){t.preventDefault();const o=e.findIndex((t=>document.activeElement===t)),r=e[o],n=t=>{const i=e[as(t,0,e.length-1)];this.focusItem(i)},a=t=>{r.expanded=t};"ArrowDown"===t.key?n(o+1):"ArrowUp"===t.key?n(o-1):i&&"ArrowRight"===t.key||s&&"ArrowLeft"===t.key?!r||r.disabled||r.expanded||r.isLeaf&&!r.lazy?n(o+1):a(!0):i&&"ArrowLeft"===t.key||s&&"ArrowRight"===t.key?!r||r.disabled||r.isLeaf||!r.expanded?n(o-1):a(!1):"Home"===t.key?n(0):"End"===t.key?n(e.length-1):"Enter"!==t.key&&" "!==t.key||r.disabled||this.selectItem(r)}}handleClick(t){const e=t.target.closest("sl-tree-item");e.disabled||this.selectItem(e)}render(){return Ht`
      <div part="base" class="tree" @click="${this.handleClick}" @keydown="${this.handleKeyDown}">
        <slot></slot>
        <slot name="expanded-icon" hidden aria-hidden="true"> </slot>
        <slot name="collapsed-icon" hidden aria-hidden="true"> </slot>
      </div>
    `}};ls.styles=Qi,ge([Ae("slot")],ls.prototype,"defaultSlot",2),ge([Ae("slot[name=expanded-icon]")],ls.prototype,"expandedIconSlot",2),ge([Ae("slot[name=collapsed-icon]")],ls.prototype,"collapsedIconSlot",2),ge([$e()],ls.prototype,"selection",2),ge([ye("selection")],ls.prototype,"handleSelectionChange",1),ls=ge([_e("sl-tree")],ls);var ds=ct`
  ${ne}

  :host {
    display: inline-block;
  }

  .checkbox {
    display: inline-flex;
    align-items: top;
    font-family: var(--sl-input-font-family);
    font-size: var(--sl-input-font-size-medium);
    font-weight: var(--sl-input-font-weight);
    color: var(--sl-input-color);
    vertical-align: middle;
    cursor: pointer;
  }

  .checkbox__control {
    flex: 0 0 auto;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: var(--sl-toggle-size);
    height: var(--sl-toggle-size);
    border: solid var(--sl-input-border-width) var(--sl-input-border-color);
    border-radius: 2px;
    background-color: var(--sl-input-background-color);
    color: var(--sl-color-neutral-0);
    transition: var(--sl-transition-fast) border-color, var(--sl-transition-fast) background-color,
      var(--sl-transition-fast) color, var(--sl-transition-fast) box-shadow;
  }

  .checkbox__input {
    position: absolute;
    opacity: 0;
    padding: 0;
    margin: 0;
    pointer-events: none;
  }

  .checkbox__control .checkbox__icon {
    display: inline-flex;
    width: var(--sl-toggle-size);
    height: var(--sl-toggle-size);
  }

  .checkbox__control .checkbox__icon svg {
    width: 100%;
    height: 100%;
  }

  /* Hover */
  .checkbox:not(.checkbox--checked):not(.checkbox--disabled) .checkbox__control:hover {
    border-color: var(--sl-input-border-color-hover);
    background-color: var(--sl-input-background-color-hover);
  }

  /* Focus */
  .checkbox:not(.checkbox--checked):not(.checkbox--disabled) .checkbox__input:focus-visible ~ .checkbox__control {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  /* Checked/indeterminate */
  .checkbox--checked .checkbox__control,
  .checkbox--indeterminate .checkbox__control {
    border-color: var(--sl-color-primary-600);
    background-color: var(--sl-color-primary-600);
  }

  /* Checked/indeterminate + hover */
  .checkbox.checkbox--checked:not(.checkbox--disabled) .checkbox__control:hover,
  .checkbox.checkbox--indeterminate:not(.checkbox--disabled) .checkbox__control:hover {
    border-color: var(--sl-color-primary-500);
    background-color: var(--sl-color-primary-500);
  }

  /* Checked/indeterminate + focus */
  .checkbox.checkbox--checked:not(.checkbox--disabled) .checkbox__input:focus-visible ~ .checkbox__control,
  .checkbox.checkbox--indeterminate:not(.checkbox--disabled) .checkbox__input:focus-visible ~ .checkbox__control {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  /* Disabled */
  .checkbox--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .checkbox__label {
    color: var(--sl-input-label-color);
    line-height: var(--sl-toggle-size);
    margin-inline-start: 0.5em;
    user-select: none;
  }

  :host([required]) .checkbox__label::after {
    content: var(--sl-input-required-content);
    margin-inline-start: var(--sl-input-required-content-offset);
  }
`,cs=class extends Event{constructor(t){super("formdata"),this.formData=t}},hs=class extends FormData{constructor(t){var e=(...t)=>{super(...t)};t?(e(t),this.form=t,t.dispatchEvent(new cs(this))):e()}append(t,e){if(!this.form)return super.append(t,e);let i=this.form.elements[t];if(i||(i=document.createElement("input"),i.type="hidden",i.name=t,this.form.appendChild(i)),this.has(t)){const s=this.getAll(t),o=s.indexOf(i.value);-1!==o&&s.splice(o,1),s.push(e),this.set(t,s)}else super.append(t,e);i.value=e}};function us(){window.FormData&&!function(){const t=document.createElement("form");let e=!1;return document.body.append(t),t.addEventListener("submit",(t=>{new FormData(t.target),t.preventDefault()})),t.addEventListener("formdata",(()=>e=!0)),t.dispatchEvent(new Event("submit",{cancelable:!0})),t.remove(),e}()&&(window.FormData=hs,window.addEventListener("submit",(t=>{t.defaultPrevented||new FormData(t.target)})))}"complete"===document.readyState?us():window.addEventListener("DOMContentLoaded",(()=>us()));var ps=new WeakMap,bs=class{constructor(t,e){(this.host=t).addController(this),this.options=fe({form:t=>t.closest("form"),name:t=>t.name,value:t=>t.value,defaultValue:t=>t.defaultValue,disabled:t=>t.disabled,reportValidity:t=>"function"!=typeof t.reportValidity||t.reportValidity(),setValue:(t,e)=>{t.value=e}},e),this.handleFormData=this.handleFormData.bind(this),this.handleFormSubmit=this.handleFormSubmit.bind(this),this.handleFormReset=this.handleFormReset.bind(this),this.reportFormValidity=this.reportFormValidity.bind(this)}hostConnected(){this.form=this.options.form(this.host),this.form&&(this.form.addEventListener("formdata",this.handleFormData),this.form.addEventListener("submit",this.handleFormSubmit),this.form.addEventListener("reset",this.handleFormReset),ps.has(this.form)||(ps.set(this.form,this.form.reportValidity),this.form.reportValidity=()=>this.reportFormValidity()))}hostDisconnected(){this.form&&(this.form.removeEventListener("formdata",this.handleFormData),this.form.removeEventListener("submit",this.handleFormSubmit),this.form.removeEventListener("reset",this.handleFormReset),ps.has(this.form)&&(this.form.reportValidity=ps.get(this.form),ps.delete(this.form)),this.form=void 0)}handleFormData(t){const e=this.options.disabled(this.host),i=this.options.name(this.host),s=this.options.value(this.host);e||"string"!=typeof i||void 0===s||(Array.isArray(s)?s.forEach((e=>{t.formData.append(i,e.toString())})):t.formData.append(i,s.toString()))}handleFormSubmit(t){const e=this.options.disabled(this.host),i=this.options.reportValidity;!this.form||this.form.noValidate||e||i(this.host)||(t.preventDefault(),t.stopImmediatePropagation())}handleFormReset(){this.options.setValue(this.host,this.options.defaultValue(this.host))}reportFormValidity(){if(this.form&&!this.form.noValidate){const t=this.form.querySelectorAll("*");for(const e of t)if("function"==typeof e.reportValidity&&!e.reportValidity())return!1}return!0}doAction(t,e){if(this.form){const i=document.createElement("button");i.type=t,i.style.position="absolute",i.style.width="0",i.style.height="0",i.style.clipPath="inset(50%)",i.style.overflow="hidden",i.style.whiteSpace="nowrap",e&&["formaction","formmethod","formnovalidate","formtarget"].forEach((t=>{e.hasAttribute(t)&&i.setAttribute(t,e.getAttribute(t))})),this.form.append(i),i.click(),i.remove()}}reset(t){this.doAction("reset",t)}submit(t){this.doAction("submit",t)}},vs=class extends oe{constructor(){super(...arguments),this.formSubmitController=new bs(this,{value:t=>t.checked?t.value||"on":void 0,defaultValue:t=>t.defaultChecked,setValue:(t,e)=>t.checked=e}),this.hasFocus=!1,this.disabled=!1,this.required=!1,this.checked=!1,this.indeterminate=!1,this.invalid=!1,this.defaultChecked=!1}firstUpdated(){this.invalid=!this.input.checkValidity()}click(){this.input.click()}focus(t){this.input.focus(t)}blur(){this.input.blur()}reportValidity(){return this.input.reportValidity()}setCustomValidity(t){this.input.setCustomValidity(t),this.invalid=!this.input.checkValidity()}handleClick(){this.checked=!this.checked,this.indeterminate=!1,ei(this,"sl-change")}handleBlur(){this.hasFocus=!1,ei(this,"sl-blur")}handleDisabledChange(){this.input.disabled=this.disabled,this.invalid=!this.input.checkValidity()}handleFocus(){this.hasFocus=!0,ei(this,"sl-focus")}handleStateChange(){this.invalid=!this.input.checkValidity()}render(){return Ht`
      <label
        part="base"
        class=${Qe({checkbox:!0,"checkbox--checked":this.checked,"checkbox--disabled":this.disabled,"checkbox--focused":this.hasFocus,"checkbox--indeterminate":this.indeterminate})}
      >
        <input
          class="checkbox__input"
          type="checkbox"
          name=${ti(this.name)}
          value=${ti(this.value)}
          .indeterminate=${ss(this.indeterminate)}
          .checked=${ss(this.checked)}
          .disabled=${this.disabled}
          .required=${this.required}
          aria-checked=${this.checked?"true":"false"}
          @click=${this.handleClick}
          @blur=${this.handleBlur}
          @focus=${this.handleFocus}
        />

        <span part="control" class="checkbox__control">
          ${this.checked?Ht`
                <svg part="checked-icon" class="checkbox__icon" viewBox="0 0 16 16">
                  <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">
                    <g stroke="currentColor" stroke-width="2">
                      <g transform="translate(3.428571, 3.428571)">
                        <path d="M0,5.71428571 L3.42857143,9.14285714"></path>
                        <path d="M9.14285714,0 L3.42857143,9.14285714"></path>
                      </g>
                    </g>
                  </g>
                </svg>
              `:""}
          ${!this.checked&&this.indeterminate?Ht`
                <svg part="indeterminate-icon" class="checkbox__icon" viewBox="0 0 16 16">
                  <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">
                    <g stroke="currentColor" stroke-width="2">
                      <g transform="translate(2.285714, 6.857143)">
                        <path d="M10.2857143,1.14285714 L1.14285714,1.14285714"></path>
                      </g>
                    </g>
                  </g>
                </svg>
              `:""}
        </span>

        <span part="label" class="checkbox__label">
          <slot></slot>
        </span>
      </label>
    `}};vs.styles=ds,ge([Ae('input[type="checkbox"]')],vs.prototype,"input",2),ge([xe()],vs.prototype,"hasFocus",2),ge([$e()],vs.prototype,"name",2),ge([$e()],vs.prototype,"value",2),ge([$e({type:Boolean,reflect:!0})],vs.prototype,"disabled",2),ge([$e({type:Boolean,reflect:!0})],vs.prototype,"required",2),ge([$e({type:Boolean,reflect:!0})],vs.prototype,"checked",2),ge([$e({type:Boolean,reflect:!0})],vs.prototype,"indeterminate",2),ge([$e({type:Boolean,reflect:!0})],vs.prototype,"invalid",2),ge([((t="value")=>(e,i)=>{const s=e.constructor,o=s.prototype.attributeChangedCallback;s.prototype.attributeChangedCallback=function(e,r,n){var a;const l=s.getPropertyOptions(t);if(e===("string"==typeof l.attribute?l.attribute:t)){const e=l.converter||vt,s=("function"==typeof e?e:null!=(a=null==e?void 0:e.fromAttribute)?a:vt.fromAttribute)(n,l.type);this[t]!==s&&(this[i]=s)}o.call(this,e,r,n)}})("checked")],vs.prototype,"defaultChecked",2),ge([ye("disabled",{waitUntilFirstUpdate:!0})],vs.prototype,"handleDisabledChange",1),ge([ye("checked",{waitUntilFirstUpdate:!0}),ye("indeterminate",{waitUntilFirstUpdate:!0})],vs.prototype,"handleStateChange",1),vs=ge([_e("sl-checkbox")],vs);var fs=ct`
  ${ne}

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
`,ms=class extends oe{constructor(){super(...arguments),this.localize=new Xe(this)}render(){return Ht`
      <svg part="base" class="spinner" role="progressbar" aria-valuetext=${this.localize.term("loading")}>
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};ms.styles=fs,ms=ge([_e("sl-spinner")],ms);var gs=ct`
  ${ne}

  :host {
    --divider-width: 4px;
    --divider-hit-area: 12px;
    --min: 0%;
    --max: 100%;

    display: grid;
  }

  .start,
  .end {
    overflow: hidden;
  }

  .divider {
    flex: 0 0 var(--divider-width);
    display: flex;
    position: relative;
    align-items: center;
    justify-content: center;
    background-color: var(--sl-color-neutral-200);
    color: var(--sl-color-neutral-900);
    z-index: 1;
  }

  .divider:focus {
    outline: none;
  }

  :host(:not([disabled])) .divider:focus-visible {
    background-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  :host([disabled]) .divider {
    cursor: not-allowed;
  }

  /* Horizontal */
  :host(:not([vertical], [disabled])) .divider {
    cursor: col-resize;
  }

  :host(:not([vertical])) .divider::after {
    display: flex;
    content: '';
    position: absolute;
    height: 100%;
    left: calc(var(--divider-hit-area) / -2 + var(--divider-width) / 2);
    width: var(--divider-hit-area);
  }

  /* Vertical */
  :host([vertical]) {
    flex-direction: column;
  }

  :host([vertical]:not([disabled])) .divider {
    cursor: row-resize;
  }

  :host([vertical]) .divider::after {
    content: '';
    position: absolute;
    width: 100%;
    top: calc(var(--divider-hit-area) / -2 + var(--divider-width) / 2);
    height: var(--divider-hit-area);
  }
`,ys=class extends oe{constructor(){super(...arguments),this.localize=new Xe(this),this.position=50,this.vertical=!1,this.disabled=!1,this.snapThreshold=12}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((t=>this.handleResize(t))),this.updateComplete.then((()=>this.resizeObserver.observe(this))),this.detectSize(),this.cachedPositionInPixels=this.percentageToPixels(this.position)}disconnectedCallback(){super.disconnectedCallback(),this.resizeObserver.unobserve(this)}detectSize(){const{width:t,height:e}=this.getBoundingClientRect();this.size=this.vertical?e:t}percentageToPixels(t){return this.size*(t/100)}pixelsToPercentage(t){return t/this.size*100}handleDrag(t){const e="rtl"===this.localize.dir();this.disabled||(t.preventDefault(),function(t,e){function i(i){const s=t.getBoundingClientRect(),o=t.ownerDocument.defaultView,r=s.left+o.pageXOffset,n=s.top+o.pageYOffset,a=i.pageX-r,l=i.pageY-n;(null==e?void 0:e.onMove)&&e.onMove(a,l)}document.addEventListener("pointermove",i,{passive:!0}),document.addEventListener("pointerup",(function t(){document.removeEventListener("pointermove",i),document.removeEventListener("pointerup",t),(null==e?void 0:e.onStop)&&e.onStop()})),(null==e?void 0:e.initialEvent)&&i(e.initialEvent)}(this,{onMove:(t,i)=>{let s=this.vertical?i:t;"end"===this.primary&&(s=this.size-s),this.snap&&this.snap.split(" ").forEach((t=>{let i;i=t.endsWith("%")?this.size*(parseFloat(t)/100):parseFloat(t),e&&!this.vertical&&(i=this.size-i),s>=i-this.snapThreshold&&s<=i+this.snapThreshold&&(s=i)})),this.position=as(this.pixelsToPercentage(s),0,100)},initialEvent:t}))}handleKeyDown(t){if(!this.disabled&&["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key)){let e=this.position;const i=(t.shiftKey?10:1)*("end"===this.primary?-1:1);t.preventDefault(),("ArrowLeft"===t.key&&!this.vertical||"ArrowUp"===t.key&&this.vertical)&&(e-=i),("ArrowRight"===t.key&&!this.vertical||"ArrowDown"===t.key&&this.vertical)&&(e+=i),"Home"===t.key&&(e="end"===this.primary?100:0),"End"===t.key&&(e="end"===this.primary?0:100),this.position=as(e,0,100)}}handlePositionChange(){this.cachedPositionInPixels=this.percentageToPixels(this.position),this.positionInPixels=this.percentageToPixels(this.position),ei(this,"sl-reposition")}handlePositionInPixelsChange(){this.position=this.pixelsToPercentage(this.positionInPixels)}handleVerticalChange(){this.detectSize()}handleResize(t){const{width:e,height:i}=t[0].contentRect;this.size=this.vertical?i:e,this.primary&&(this.position=this.pixelsToPercentage(this.cachedPositionInPixels))}render(){const t=this.vertical?"gridTemplateRows":"gridTemplateColumns",e=this.vertical?"gridTemplateColumns":"gridTemplateRows",i="rtl"===this.localize.dir(),s=`\n      clamp(\n        0%,\n        clamp(\n          var(--min),\n          ${this.position}% - var(--divider-width) / 2,\n          var(--max)\n        ),\n        calc(100% - var(--divider-width))\n      )\n    `;return"end"===this.primary?i&&!this.vertical?this.style[t]=`${s} var(--divider-width) auto`:this.style[t]=`auto var(--divider-width) ${s}`:i&&!this.vertical?this.style[t]=`auto var(--divider-width) ${s}`:this.style[t]=`${s} var(--divider-width) auto`,this.style[e]="",Ht`
      <div part="panel start" class="start">
        <slot name="start"></slot>
      </div>

      <div
        part="divider"
        class="divider"
        tabindex=${ti(this.disabled?void 0:"0")}
        role="separator"
        aria-label=${this.localize.term("resize")}
        @keydown=${this.handleKeyDown}
        @mousedown=${this.handleDrag}
        @touchstart=${this.handleDrag}
      >
        <slot name="handle"></slot>
      </div>

      <div part="panel end" class="end">
        <slot name="end"></slot>
      </div>
    `}};ys.styles=gs,ge([Ae(".divider")],ys.prototype,"divider",2),ge([$e({type:Number,reflect:!0})],ys.prototype,"position",2),ge([$e({attribute:"position-in-pixels",type:Number})],ys.prototype,"positionInPixels",2),ge([$e({type:Boolean,reflect:!0})],ys.prototype,"vertical",2),ge([$e({type:Boolean,reflect:!0})],ys.prototype,"disabled",2),ge([$e()],ys.prototype,"primary",2),ge([$e()],ys.prototype,"snap",2),ge([$e({type:Number,attribute:"snap-threshold"})],ys.prototype,"snapThreshold",2),ge([ye("position")],ys.prototype,"handlePositionChange",1),ge([ye("positionInPixels")],ys.prototype,"handlePositionInPixelsChange",1),ge([ye("vertical")],ys.prototype,"handleVerticalChange",1),ys=ge([_e("sl-split-panel")],ys);class _s extends it{static styles=r`
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
  `;static properties={path:{type:String},_visible:{type:Boolean,state:!0}};connectedCallback(){super.connectedCallback(),this.observer=new IntersectionObserver(((t,e)=>{t.forEach((t=>{t.isIntersecting?this._visible=!0:this._visible=!1}))})),this.observer.observe(this.parentElement)}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}constructor(){super(),this._visible=!1}hideLoading(){this.renderRoot.querySelector("#loading").style.display="none"}render(){return this._visible?D`
                <div id="loading" class="loading">
                    <sl-spinner></sl-spinner>
                </div>
                <div class="plot">
                    <iframe @load=${this.hideLoading} seamless frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
                </div>
            `:D``}}customElements.define("sc-diagram",_s);var ws=ct`
  ${ne}

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

  .button:focus-visible {
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

  .button--text:focus-visible:not(.button--disabled) {
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

  .button--rtl ::slotted(sl-badge) {
    right: auto;
    left: 0;
    transform: translateY(-50%) translateX(-50%);
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
    padding-inline-start: var(--sl-spacing-x-small);
  }

  .button--has-prefix.button--small .button__label {
    padding-inline-start: var(--sl-spacing-x-small);
  }

  .button--has-prefix.button--medium {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-prefix.button--medium .button__label {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-prefix.button--large {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-prefix.button--large .button__label {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-suffix.button--small,
  .button--caret.button--small {
    padding-inline-end: var(--sl-spacing-x-small);
  }

  .button--has-suffix.button--small .button__label,
  .button--caret.button--small .button__label {
    padding-inline-end: var(--sl-spacing-x-small);
  }

  .button--has-suffix.button--medium,
  .button--caret.button--medium {
    padding-inline-end: var(--sl-spacing-small);
  }

  .button--has-suffix.button--medium .button__label,
  .button--caret.button--medium .button__label {
    padding-inline-end: var(--sl-spacing-small);
  }

  .button--has-suffix.button--large,
  .button--caret.button--large {
    padding-inline-end: var(--sl-spacing-small);
  }

  .button--has-suffix.button--large .button__label,
  .button--caret.button--large .button__label {
    padding-inline-end: var(--sl-spacing-small);
  }

  /*
   * Button groups support a variety of button types (e.g. buttons with tooltips, buttons as dropdown triggers, etc.).
   * This means buttons aren't always direct descendants of the button group, thus we can't target them with the
   * ::slotted selector. To work around this, the button group component does some magic to add these special classes to
   * buttons and we style them here instead.
   */

  :host(.sl-button-group__button--first:not(.sl-button-group__button--last)) .button {
    border-start-end-radius: 0;
    border-end-end-radius: 0;
  }

  :host(.sl-button-group__button--inner) .button {
    border-radius: 0;
  }

  :host(.sl-button-group__button--last:not(.sl-button-group__button--first)) .button {
    border-start-start-radius: 0;
    border-end-start-radius: 0;
  }

  /* All except the first */
  :host(.sl-button-group__button:not(.sl-button-group__button--first)) {
    margin-inline-start: calc(-1 * var(--sl-input-border-width));
  }

  /* Add a visual separator between solid buttons */
  :host(.sl-button-group__button:not(.sl-button-group__button--focus, .sl-button-group__button--first, .sl-button-group__button--radio, [variant='default']):not(:hover, :active, :focus))
    .button:after {
    content: '';
    position: absolute;
    top: 0;
    inset-inline-start: 0;
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
`,$s=class extends oe{constructor(){super(...arguments),this.formSubmitController=new bs(this,{form:t=>{if(t.hasAttribute("form")){const e=t.getRootNode(),i=t.getAttribute("form");return e.getElementById(i)}return t.closest("form")}}),this.hasSlotController=new Ze(this,"[default]","prefix","suffix"),this.localize=new Xe(this),this.hasFocus=!1,this.variant="default",this.size="medium",this.caret=!1,this.disabled=!1,this.loading=!1,this.outline=!1,this.pill=!1,this.circle=!1,this.type="button"}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,ei(this,"sl-blur")}handleFocus(){this.hasFocus=!0,ei(this,"sl-focus")}handleClick(t){if(this.disabled||this.loading)return t.preventDefault(),void t.stopPropagation();"submit"===this.type&&this.formSubmitController.submit(this),"reset"===this.type&&this.formSubmitController.reset(this)}render(){const t=!!this.href,e=t?ai`a`:ai`button`;return ci`
      <${e}
        part="base"
        class=${Qe({button:!0,"button--default":"default"===this.variant,"button--primary":"primary"===this.variant,"button--success":"success"===this.variant,"button--neutral":"neutral"===this.variant,"button--warning":"warning"===this.variant,"button--danger":"danger"===this.variant,"button--text":"text"===this.variant,"button--small":"small"===this.size,"button--medium":"medium"===this.size,"button--large":"large"===this.size,"button--caret":this.caret,"button--circle":this.circle,"button--disabled":this.disabled,"button--focused":this.hasFocus,"button--loading":this.loading,"button--standard":!this.outline,"button--outline":this.outline,"button--pill":this.pill,"button--rtl":"rtl"===this.localize.dir(),"button--has-label":this.hasSlotController.test("[default]"),"button--has-prefix":this.hasSlotController.test("prefix"),"button--has-suffix":this.hasSlotController.test("suffix")})}
        ?disabled=${ti(t?void 0:this.disabled)}
        type=${ti(t?void 0:this.type)}
        name=${ti(t?void 0:this.name)}
        value=${ti(t?void 0:this.value)}
        href=${ti(t?this.href:void 0)}
        target=${ti(t?this.target:void 0)}
        download=${ti(t?this.download:void 0)}
        rel=${ti(t&&this.target?"noreferrer noopener":void 0)}
        role=${ti(t?void 0:"button")}
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
        ${this.caret?ci`
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
        ${this.loading?ci`<sl-spinner></sl-spinner>`:""}
      </${e}>
    `}};$s.styles=ws,ge([Ae(".button")],$s.prototype,"button",2),ge([xe()],$s.prototype,"hasFocus",2),ge([$e({reflect:!0})],$s.prototype,"variant",2),ge([$e({reflect:!0})],$s.prototype,"size",2),ge([$e({type:Boolean,reflect:!0})],$s.prototype,"caret",2),ge([$e({type:Boolean,reflect:!0})],$s.prototype,"disabled",2),ge([$e({type:Boolean,reflect:!0})],$s.prototype,"loading",2),ge([$e({type:Boolean,reflect:!0})],$s.prototype,"outline",2),ge([$e({type:Boolean,reflect:!0})],$s.prototype,"pill",2),ge([$e({type:Boolean,reflect:!0})],$s.prototype,"circle",2),ge([$e()],$s.prototype,"type",2),ge([$e()],$s.prototype,"name",2),ge([$e()],$s.prototype,"value",2),ge([$e()],$s.prototype,"href",2),ge([$e()],$s.prototype,"target",2),ge([$e()],$s.prototype,"download",2),ge([$e()],$s.prototype,"form",2),ge([$e({attribute:"formaction"})],$s.prototype,"formAction",2),ge([$e({attribute:"formmethod"})],$s.prototype,"formMethod",2),ge([$e({attribute:"formnovalidate",type:Boolean})],$s.prototype,"formNoValidate",2),ge([$e({attribute:"formtarget"})],$s.prototype,"formTarget",2),$s=ge([_e("sl-button")],$s);var xs=ct`
  ${ne}

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

  .details__header:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: calc(1px + var(--sl-focus-ring-offset));
  }

  .details--disabled .details__header {
    cursor: not-allowed;
  }

  .details--disabled .details__header:focus-visible {
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
`,ks=class extends oe{constructor(){super(...arguments),this.localize=new Xe(this),this.open=!1,this.disabled=!1}firstUpdated(){this.body.hidden=!this.open,this.body.style.height=this.open?"auto":"0"}async show(){if(!this.open&&!this.disabled)return this.open=!0,ii(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,ii(this,"sl-after-hide")}handleSummaryClick(){this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){ei(this,"sl-show"),await Oe(this.body),this.body.hidden=!1;const{keyframes:t,options:e}=Re(this,"details.show",{dir:this.localize.dir()});await Ue(this.body,De(t,this.body.scrollHeight),e),this.body.style.height="auto",ei(this,"sl-after-show")}else{ei(this,"sl-hide"),await Oe(this.body);const{keyframes:t,options:e}=Re(this,"details.hide",{dir:this.localize.dir()});await Ue(this.body,De(t,this.body.scrollHeight),e),this.body.hidden=!0,this.body.style.height="auto",ei(this,"sl-after-hide")}}render(){return Ht`
      <div
        part="base"
        class=${Qe({details:!0,"details--open":this.open,"details--disabled":this.disabled})}
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
    `}};ks.styles=xs,ge([Ae(".details")],ks.prototype,"details",2),ge([Ae(".details__header")],ks.prototype,"header",2),ge([Ae(".details__body")],ks.prototype,"body",2),ge([$e({type:Boolean,reflect:!0})],ks.prototype,"open",2),ge([$e()],ks.prototype,"summary",2),ge([$e({type:Boolean,reflect:!0})],ks.prototype,"disabled",2),ge([ye("open",{waitUntilFirstUpdate:!0})],ks.prototype,"handleOpenChange",1),ks=ge([_e("sl-details")],ks),Me("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),Me("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}});class As extends it{static styles=r`
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
    `;static properties={title:{type:String},paths:{type:Object},diff:{type:String}};getFileContents(t){return new Promise((function(e,i){fetch(t).then((t=>{if(!t.ok)throw new Error(`HTTP error: status ${t.status}`);return t.blob()})).then((t=>t.text())).then((t=>{e(t)}))}))}getNewTabBtnTemplate(t){return D`
            <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${t} target="_blank">
                Open in New Tab
            </sl-button>
        `}getDiffTemplate(){if(this.diff){const t=`${this.title}-diff`;return D`
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
            `}return D``}getTabTemplate(t,e){const i=`details-panel-${this.title}-${t}`;return D`
            <sl-tab class="tab" slot="nav" panel=${i}>${t}</sl-tab>
            <sl-tab-panel class="tab-panel" name=${i}>
                <div class="text-field-container">
                    <div>
                        ${this.getNewTabBtnTemplate(e)}
                    </div>
                    <pre><code>${Fi(this.getFileContents(e),D`Loading...`)}</code></pre>
                </div>
            </sl-tab-panel>
        `}render(){return D`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.paths).map((t=>this.getTabTemplate(t[0],t[1])))}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `}}customElements.define("sc-file-preview",As);class Cs{}const Es=new WeakMap,Ss=Si(class extends Oi{render(t){return N}update(t,[e]){var i;const s=e!==this.Y;return s&&void 0!==this.Y&&this.rt(void 0),(s||this.lt!==this.dt)&&(this.Y=e,this.ct=null===(i=t.options)||void 0===i?void 0:i.host,this.rt(this.dt=t.element)),N}rt(t){var e;if("function"==typeof this.Y){const i=null!==(e=this.ct)&&void 0!==e?e:globalThis;let s=Es.get(i);void 0===s&&(s=new WeakMap,Es.set(i,s)),void 0!==s.get(this.Y)&&this.Y.call(this.ct,void 0),s.set(this.Y,t),void 0!==t&&this.Y.call(this.ct,t)}else this.Y.value=t}get lt(){var t,e,i;return"function"==typeof this.Y?null===(e=Es.get(null!==(t=this.ct)&&void 0!==t?t:globalThis))||void 0===e?void 0:e.get(this.Y):null===(i=this.Y)||void 0===i?void 0:i.value}disconnected(){this.lt===this.dt&&this.rt(void 0)}reconnected(){this.rt(this.dt)}});class Ts extends Ri{static styles=[Ri.styles,r`
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
        `];tableRef=(()=>new Cs)();removeDetailsEl(t){for(const e of t.childNodes)if("TR"===e.tagName)for(const t of e.childNodes)for(const e of t.childNodes)"SL-DETAILS"===e.tagName&&t.removeChild(e);return t}copyTable(){const t=window.getSelection();t.removeAllRanges();const e=document.createRange();e.selectNodeContents(this.tableRef.value),t.addRange(e),this.removeDetailsEl(t.anchorNode),document.execCommand("copy"),t.removeAllRanges(),this.requestUpdate()}parseMetric(t){const e=t[0].split("|");return D`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,i]=t.split("|");return D`
            <td class="td-value">
                ${i?D`<abbr title=${i}>${e}</abbr>`:D`${e}`}
            </td>
        `}async parseSrc(){let t,e=D``;for await(const i of this.makeTextFileLineIterator(this.file)){const s=i.split(";"),o=s[0];if(s.shift(),"H"===o)for(const t of s)e=D`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===o)t=this.parseMetric(s);else{const i=D`${s.map((t=>this.parseSummaryFunc(t)))}`;e=D`
                    ${e}
                    <tr>
                      ${t}
                      ${i}
                    </tr>
                `,t&&(t=void 0)}}return e=D`<table ${Ss(this.tableRef)} width=${this.getWidth(this.cols)}>${e}</table>`,D`
            <div style="display:flex;">
                ${e}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}}customElements.define("sc-smry-tbl",Ts);class zs extends it{static styles=r`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},fpreviews:{type:Array},smrytblpath:{type:String},smrytblfile:{type:Blob}};render(){return this.smrytblpath&&!this.smrytblfile&&fetch(this.smrytblpath).then((t=>t.blob())).then((t=>{this.smrytblfile=t})),D`
            <br>
            ${this.smrytblfile?D`<sc-smry-tbl .file="${this.smrytblfile}"></sc-smry-tbl>`:D``}
            ${this.fpreviews?this.fpreviews.map((t=>D`
                    <sc-file-preview .title=${t.title} .diff=${t.diff} .paths=${t.paths}></sc-file-preview>
                    <br>
                `)):D``}
            <div class="grid">
                ${this.paths?this.paths.map((t=>D`
                    <sc-diagram path="${t}"></sc-diagram>
                    `)):D``}
            </div>
        `}}customElements.define("sc-data-tab",zs);class Ps extends it{static styles=r`
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
    `;static properties={tabs:{type:Object}};convertToSelector(t){return t.replace(/\s/g,"-").replace(/[^a-zA-Z0-9-]+/g,"")}selectTabInTabTree(t){let e=this.renderRoot.querySelector(`${t}-tree`);for(e.selected=!0;"SL-TREE-ITEM"===e.tagName;)e.expanded=!0,e=e.parentElement}updateVisibleTab(t=location.hash){this.currentEl&&(this.currentEl.hidden=!0);const e=this.renderRoot.querySelector(t);this.currentEl=e,e&&(e.hidden=!1),this.selectTabInTabTree(t)}firstUpdated(){let t=location.hash;if(!t)return t=`#${this.firstTab}`,void(location.hash=t);const e=this.renderRoot.querySelector("sl-tab-group");e.updateComplete.then((()=>{e.show(this.subtabs[t.substring(1)])})),this.updateVisibleTab()}connectedCallback(){super.connectedCallback(),this.hashHandler=()=>{this.updateVisibleTab()},window.addEventListener("hashchange",this.hashHandler,!1)}disconnectedCallback(){window.removeEventListener("hashchange",this.hashHandler)}tabPanesTemplate(t){let e=D``;for(const i of t.tabs)e=i.tabs?D`${e}${this.tabPanesTemplate(i)}`:D`${e}<sc-data-tab hidden id="${this.convertToSelector(i.name)}" tabname=${i.name} .smrytblpath=${i.smrytblpath} .smrytblfile=${i.smrytblfile} .paths=${i.ppaths} .fpreviews=${i.fpreviews} .dir=${i.dir}></sc-data-tab>`;return e}treeItemTemplate(t,e){if(!t.tabs){const i=this.convertToSelector(t.name);return this.subtabs[i]=e,this.firstTab||(this.firstTab=i),t.name}return D`
                ${t.name}
                ${t.tabs.map((t=>{const i=this.convertToSelector(t.name);return D`
                        <sl-tree-item id=${`${i}-tree`} @click=${t.tabs?()=>{}:()=>{location.hash=i}}>
                            ${this.treeItemTemplate(t,e)}
                        </sl-tree-item>
                    `}))}
        `}render(){return this.tabs?D`
            <sl-tab-group>
                ${this.tabs.map((t=>D`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">
                        <sl-split-panel position=20 style="--divider-width: 20px;">
                            <sl-tree selection="leaf" slot="start">
                                ${this.treeItemTemplate(t,t.name)}
                            </sl-tree>
                            <div style="height: 95vh; overflow:scroll;" slot="end">
                                ${this.tabPanesTemplate(t)}
                            </div>
                        </sl-split-panel>
                    </sl-tab-panel>
                `))}
            </sl-tab-group>
      `:D``}constructor(){super(),this.subtabs={},this.firstTab=""}}customElements.define("sc-tab-group",Ps);class Ls extends it{static properties={introtbl:{type:Object},src:{type:String},reportInfo:{type:Object},toolname:{type:String},titleDescr:{type:String},tabs:{type:Object},fetchFailed:{type:Boolean,attribute:!1}};static styles=r`
        .report-head {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .report-title {
            font-family: Arial, sans-serif;
        }

        .cors-warning {
            display: flex;
            flex-direction: column;
            font-family: Arial, sans-serif;
        }

        .sticky {
            position: sticky;
            top: 0;
            height: 100vh;
        }

        // Hide the close button as the dialog is not closable.
        sl-dialog::part(close-button) {
            visibility: hidden;
        }
    `;get _corsWarning(){return this.renderRoot.querySelector(".cors-warning")}initRepProps(){this.toolname=this.reportInfo.toolname,this.titleDescr=this.reportInfo.title_descr}parseReportInfo(t){this.reportInfo=t,this.initRepProps(),fetch(t.intro_tbl).then((t=>t.blob())).then((t=>{this.introtbl=t})),fetch(t.tab_file).then((t=>t.json())).then((async t=>{this.tabs=t}))}connectedCallback(){fetch(this.src).then((t=>t.json())).then((t=>this.parseReportInfo(t))).catch((t=>{if(!(t instanceof TypeError))throw t;this.fetchFailed=!0})),super.connectedCallback()}updated(t){t.has("fetchFailed")&&this.fetchFailed&&this._corsWarning.addEventListener("sl-request-close",(t=>{t.preventDefault()}))}corsWarning(){return D`
            <sl-dialog class="cors-warning" label="Failed to load report" open>
                <p>
                    Due to browser security limitations your report could not be retrieved. Please
                    upload your report directory using the upload button below:
                </p>
                <input @change="${this.processUploadedFiles}" id="upload-files" directory webkitdirectory type="file">
                <sl-divider></sl-divider>
                <p>
                    If you have tried uploading your report directory with the button above and it 
                    is still not rendering properly, please see our documentation for details on
                    other methods for viewing wult reports:
                    <a href="https://intel.github.io/wult/pages/howto-view-local.html#open-wult-reports-locally"> here</a>.
                </p>
            </sl-dialog>
        `}findFile(t){const e=Object.keys(this.files);for(const i of e)if(i.endsWith(t))return this.files[i];throw Error(`unable to find an uploaded file ending with '${t}'.`)}async extractTabs(t,e){for(const i of t)i.smrytblpath&&(i.smrytblfile=e?await fetch(i.smrytblpath).then((t=>t.blob())):this.findFile(i.smrytblpath)),i.tabs&&(i.tabs=await this.extractTabs(i.tabs,e));return t}async processUploadedFiles(){const t=this.renderRoot.getElementById("upload-files");this.files={};for(const e of t.files)this.files[e.webkitRelativePath]=e;const e=await this.findFile("report_info.json").arrayBuffer();this.reportInfo=JSON.parse((new TextDecoder).decode(e)),this.introtbl=this.findFile(this.reportInfo.intro_tbl);const i=await this.findFile(this.reportInfo.tab_file).arrayBuffer().then((t=>JSON.parse((new TextDecoder).decode(t))));this.tabs=await this.extractTabs(i,!1),this.initRepProps(),this.fetchFailed=!1}constructor(){super(),this.fetchFailed=!1,this.reportInfo={}}render(){return this.fetchFailed?this.corsWarning():D`
            <div class="report-head">
                ${this.toolname?D`<h1 class="report-title">${this.toolname} report</h1>`:D``}
                ${this.titleDescr?D`
                        <p class="title_descr">${this.titleDescr}</p>
                        <br>
                    `:D``}
                ${this.introtbl?D`<sc-intro-tbl .file=${this.introtbl}></sc-intro-tbl>`:D``}
            </div>
            <br>
            <div class="sticky">
                ${this.tabs?D`<sc-tab-group .tabs=${this.tabs}></sc-tab-group>`:D``}
            </div>
        `}}customElements.define("sc-report-page",Ls),pi("shoelace")})();