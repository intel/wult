/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window,e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,o=Symbol(),s=new WeakMap;class i{constructor(t,e,s){if(this._$cssResult$=!0,s!==o)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const o=this.t;if(e&&void 0===t){const e=void 0!==o&&1===o.length;e&&(t=s.get(o)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&s.set(o,t))}return t}toString(){return this.cssText}}const r=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,o,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(o)+t[s+1]),t[0]);return new i(s,t,o)},n=e?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const o of t.cssRules)e+=o.cssText;return(t=>new i("string"==typeof t?t:t+"",void 0,o))(e)})(t):t;var a;const l=window,d=l.trustedTypes,c=d?d.emptyScript:"",h=l.reactiveElementPolyfillSupport,u={toAttribute(t,e){switch(e){case Boolean:t=t?c:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let o=t;switch(e){case Boolean:o=null!==t;break;case Number:o=null===t?null:Number(t);break;case Object:case Array:try{o=JSON.parse(t)}catch(t){o=null}}return o}},p=(t,e)=>e!==t&&(e==e||t==t),b={attribute:!0,type:String,converter:u,reflect:!1,hasChanged:p};class v extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this.u()}static addInitializer(t){var e;null!==(e=this.h)&&void 0!==e||(this.h=[]),this.h.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,o)=>{const s=this._$Ep(o,e);void 0!==s&&(this._$Ev.set(s,o),t.push(s))})),t}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const o="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,o,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,o){return{get(){return this[e]},set(s){const i=this[t];this[e]=s,this.requestUpdate(t,i,o)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||b}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const o of e)this.createProperty(o,t[o])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const o=new Set(t.flat(1/0).reverse());for(const t of o)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Ep(t,e){const o=e.attribute;return!1===o?void 0:"string"==typeof o?o:"string"==typeof t?t.toLowerCase():void 0}u(){var t;this._$E_=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,o;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(o=t.hostConnected)||void 0===o||o.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])}))}createRenderRoot(){var o;const s=null!==(o=this.shadowRoot)&&void 0!==o?o:this.attachShadow(this.constructor.shadowRootOptions);return((o,s)=>{e?o.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((e=>{const s=document.createElement("style"),i=t.litNonce;void 0!==i&&s.setAttribute("nonce",i),s.textContent=e.cssText,o.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,o){this._$AK(t,o)}_$EO(t,e,o=b){var s;const i=this.constructor._$Ep(t,o);if(void 0!==i&&!0===o.reflect){const r=(void 0!==(null===(s=o.converter)||void 0===s?void 0:s.toAttribute)?o.converter:u).toAttribute(e,o.type);this._$El=t,null==r?this.removeAttribute(i):this.setAttribute(i,r),this._$El=null}}_$AK(t,e){var o;const s=this.constructor,i=s._$Ev.get(t);if(void 0!==i&&this._$El!==i){const t=s.getPropertyOptions(i),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(o=t.converter)||void 0===o?void 0:o.fromAttribute)?t.converter:u;this._$El=i,this[i]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,o){let s=!0;void 0!==t&&(((o=o||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===o.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,o))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach(((t,e)=>this[e]=t)),this._$Ei=void 0);let e=!1;const o=this._$AL;try{e=this.shouldUpdate(o),e?(this.willUpdate(o),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(o)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(o)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$EO(e,this[e],t))),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}}var f;v.finalized=!0,v.elementProperties=new Map,v.elementStyles=[],v.shadowRootOptions={mode:"open"},null==h||h({ReactiveElement:v}),(null!==(a=l.reactiveElementVersions)&&void 0!==a?a:l.reactiveElementVersions=[]).push("1.4.1");const g=window,m=g.trustedTypes,y=m?m.createPolicy("lit-html",{createHTML:t=>t}):void 0,_=`lit$${(Math.random()+"").slice(9)}$`,$="?"+_,w=`<${$}>`,A=document,x=(t="")=>A.createComment(t),C=t=>null===t||"object"!=typeof t&&"function"!=typeof t,k=Array.isArray,S=t=>k(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]),E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,T=/-->/g,P=/>/g,z=RegExp(">|[ \t\n\f\r](?:([^\\s\"'>=/]+)([ \t\n\f\r]*=[ \t\n\f\r]*(?:[^ \t\n\f\r\"'`<>=]|(\"|')|))|$)","g"),U=/'/g,L=/"/g,H=/^(?:script|style|textarea|title)$/i,N=t=>(e,...o)=>({_$litType$:t,strings:e,values:o}),O=N(1),M=(N(2),Symbol.for("lit-noChange")),D=Symbol.for("lit-nothing"),R=new WeakMap,F=A.createTreeWalker(A,129,null,!1),B=(t,e)=>{const o=t.length-1,s=[];let i,r=2===e?"<svg>":"",n=E;for(let e=0;e<o;e++){const o=t[e];let a,l,d=-1,c=0;for(;c<o.length&&(n.lastIndex=c,l=n.exec(o),null!==l);)c=n.lastIndex,n===E?"!--"===l[1]?n=T:void 0!==l[1]?n=P:void 0!==l[2]?(H.test(l[2])&&(i=RegExp("</"+l[2],"g")),n=z):void 0!==l[3]&&(n=z):n===z?">"===l[0]?(n=null!=i?i:E,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?z:'"'===l[3]?L:U):n===L||n===U?n=z:n===T||n===P?n=E:(n=z,i=void 0);const h=n===z&&t[e+1].startsWith("/>")?" ":"";r+=n===E?o+w:d>=0?(s.push(a),o.slice(0,d)+"$lit$"+o.slice(d)+_+h):o+_+(-2===d?(s.push(void 0),e):h)}const a=r+(t[o]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==y?y.createHTML(a):a,s]};class I{constructor({strings:t,_$litType$:e},o){let s;this.parts=[];let i=0,r=0;const n=t.length-1,a=this.parts,[l,d]=B(t,e);if(this.el=I.createElement(l,o),F.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=F.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(_)){const o=d[r++];if(t.push(e),void 0!==o){const t=s.getAttribute(o.toLowerCase()+"$lit$").split(_),e=/([.?@])?(.*)/.exec(o);a.push({type:1,index:i,name:e[2],strings:t,ctor:"."===e[1]?K:"?"===e[1]?X:"@"===e[1]?Z:q})}else a.push({type:6,index:i})}for(const e of t)s.removeAttribute(e)}if(H.test(s.tagName)){const t=s.textContent.split(_),e=t.length-1;if(e>0){s.textContent=m?m.emptyScript:"";for(let o=0;o<e;o++)s.append(t[o],x()),F.nextNode(),a.push({type:2,index:++i});s.append(t[e],x())}}}else if(8===s.nodeType)if(s.data===$)a.push({type:2,index:i});else{let t=-1;for(;-1!==(t=s.data.indexOf(_,t+1));)a.push({type:7,index:i}),t+=_.length-1}i++}}static createElement(t,e){const o=A.createElement("template");return o.innerHTML=t,o}}function j(t,e,o=t,s){var i,r,n,a;if(e===M)return e;let l=void 0!==s?null===(i=o._$Cl)||void 0===i?void 0:i[s]:o._$Cu;const d=C(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,o,s)),void 0!==s?(null!==(n=(a=o)._$Cl)&&void 0!==n?n:a._$Cl=[])[s]=l:o._$Cu=l),void 0!==l&&(e=j(t,l._$AS(t,e.values),l,s)),e}class V{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:o},parts:s}=this._$AD,i=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:A).importNode(o,!0);F.currentNode=i;let r=F.nextNode(),n=0,a=0,l=s[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new W(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new J(r,this,t)),this.v.push(e),l=s[++a]}n!==(null==l?void 0:l.index)&&(r=F.nextNode(),n++)}return i}m(t){let e=0;for(const o of this.v)void 0!==o&&(void 0!==o.strings?(o._$AI(t,o,e),e+=o.strings.length-2):o._$AI(t[e])),e++}}class W{constructor(t,e,o,s){var i;this.type=2,this._$AH=D,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=o,this.options=s,this._$C_=null===(i=null==s?void 0:s.isConnected)||void 0===i||i}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$C_}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=j(this,t,e),C(t)?t===D||null==t||""===t?(this._$AH!==D&&this._$AR(),this._$AH=D):t!==this._$AH&&t!==M&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):S(t)?this.O(t):this.$(t)}S(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.S(t))}$(t){this._$AH!==D&&C(this._$AH)?this._$AA.nextSibling.data=t:this.k(A.createTextNode(t)),this._$AH=t}T(t){var e;const{values:o,_$litType$:s}=t,i="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=I.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===i)this._$AH.m(o);else{const t=new V(i,this),e=t.p(this.options);t.m(o),this.k(e),this._$AH=t}}_$AC(t){let e=R.get(t.strings);return void 0===e&&R.set(t.strings,e=new I(t)),e}O(t){k(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let o,s=0;for(const i of t)s===e.length?e.push(o=new W(this.S(x()),this.S(x()),this,this.options)):o=e[s],o._$AI(i),s++;s<e.length&&(this._$AR(o&&o._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var o;for(null===(o=this._$AP)||void 0===o||o.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$C_=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class q{constructor(t,e,o,s,i){this.type=1,this._$AH=D,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=i,o.length>2||""!==o[0]||""!==o[1]?(this._$AH=Array(o.length-1).fill(new String),this.strings=o):this._$AH=D}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,o,s){const i=this.strings;let r=!1;if(void 0===i)t=j(this,t,e,0),r=!C(t)||t!==this._$AH&&t!==M,r&&(this._$AH=t);else{const s=t;let n,a;for(t=i[0],n=0;n<i.length-1;n++)a=j(this,s[o+n],e,n),a===M&&(a=this._$AH[n]),r||(r=!C(a)||a!==this._$AH[n]),a===D?t=D:t!==D&&(t+=(null!=a?a:"")+i[n+1]),this._$AH[n]=a}r&&!s&&this.P(t)}P(t){t===D?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class K extends q{constructor(){super(...arguments),this.type=3}P(t){this.element[this.name]=t===D?void 0:t}}const Y=m?m.emptyScript:"";class X extends q{constructor(){super(...arguments),this.type=4}P(t){t&&t!==D?this.element.setAttribute(this.name,Y):this.element.removeAttribute(this.name)}}class Z extends q{constructor(t,e,o,s,i){super(t,e,o,s,i),this.type=5}_$AI(t,e=this){var o;if((t=null!==(o=j(this,t,e,0))&&void 0!==o?o:D)===M)return;const s=this._$AH,i=t===D&&s!==D||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==D&&(s===D||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,o;"function"==typeof this._$AH?this._$AH.call(null!==(o=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==o?o:this.element,t):this._$AH.handleEvent(t)}}class J{constructor(t,e,o){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=o}get _$AU(){return this._$AM._$AU}_$AI(t){j(this,t)}}const G={A:"$lit$",M:_,C:$,L:1,R:B,D:V,V:S,I:j,H:W,N:q,U:X,B:Z,F:K,W:J},Q=g.litHtmlPolyfillSupport;var tt,et;null==Q||Q(I,W),(null!==(f=g.litHtmlVersions)&&void 0!==f?f:g.litHtmlVersions=[]).push("2.3.1");class ot extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const o=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=o.firstChild),o}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,o)=>{var s,i;const r=null!==(s=null==o?void 0:o.renderBefore)&&void 0!==s?s:e;let n=r._$litPart$;if(void 0===n){const t=null!==(i=null==o?void 0:o.renderBefore)&&void 0!==i?i:null;r._$litPart$=n=new W(e.insertBefore(x(),t),t,void 0,null!=o?o:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return M}}ot.finalized=!0,ot._$litElement$=!0,null===(tt=globalThis.litElementHydrateSupport)||void 0===tt||tt.call(globalThis,{LitElement:ot});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:ot}),(null!==(et=globalThis.litElementVersions)&&void 0!==et?et:globalThis.litElementVersions=[]).push("3.2.2");var it,rt,nt=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,at=Symbol(),lt=new Map,dt=class{constructor(t,e){if(this._$cssResult$=!0,e!==at)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=lt.get(this.cssText);return nt&&void 0===t&&(lt.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},ct=(t,...e)=>{const o=1===t.length?t[0]:e.reduce(((e,o,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(o)+t[s+1]),t[0]);return new dt(o,at)},ht=nt?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const o of t.cssRules)e+=o.cssText;return(t=>new dt("string"==typeof t?t:t+"",at))(e)})(t):t,ut=window.trustedTypes,pt=ut?ut.emptyScript:"",bt=window.reactiveElementPolyfillSupport,vt={toAttribute(t,e){switch(e){case Boolean:t=t?pt:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let o=t;switch(e){case Boolean:o=null!==t;break;case Number:o=null===t?null:Number(t);break;case Object:case Array:try{o=JSON.parse(t)}catch(t){o=null}}return o}},ft=(t,e)=>e!==t&&(e==e||t==t),gt={attribute:!0,type:String,converter:vt,reflect:!1,hasChanged:ft},mt=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,o)=>{const s=this._$Eh(o,e);void 0!==s&&(this._$Eu.set(s,o),t.push(s))})),t}static createProperty(t,e=gt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const o="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,o,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,o){return{get(){return this[e]},set(s){const i=this[t];this[e]=s,this.requestUpdate(t,i,o)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||gt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const o of e)this.createProperty(o,t[o])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const o=new Set(t.flat(1/0).reverse());for(const t of o)e.unshift(ht(t))}else void 0!==t&&e.push(ht(t));return e}static _$Eh(t,e){const o=e.attribute;return!1===o?void 0:"string"==typeof o?o:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,o;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(o=t.hostConnected)||void 0===o||o.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return o=e,s=this.constructor.elementStyles,nt?o.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const e=document.createElement("style"),s=window.litNonce;void 0!==s&&e.setAttribute("nonce",s),e.textContent=t.cssText,o.appendChild(e)})),e;var o,s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,o){this._$AK(t,o)}_$ES(t,e,o=gt){var s,i;const r=this.constructor._$Eh(t,o);if(void 0!==r&&!0===o.reflect){const n=(null!==(i=null===(s=o.converter)||void 0===s?void 0:s.toAttribute)&&void 0!==i?i:vt.toAttribute)(e,o.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var o,s,i;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),a=t.converter,l=null!==(i=null!==(s=null===(o=a)||void 0===o?void 0:o.fromAttribute)&&void 0!==s?s:"function"==typeof a?a:null)&&void 0!==i?i:vt.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,o){let s=!0;void 0!==t&&(((o=o||this.constructor.getPropertyOptions(t)).hasChanged||ft)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===o.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,o))):s=!1),!this.isUpdatePending&&s&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const o=this._$AL;try{e=this.shouldUpdate(o),e?(this.willUpdate(o),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(o)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(o)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}};mt.finalized=!0,mt.elementProperties=new Map,mt.elementStyles=[],mt.shadowRootOptions={mode:"open"},null==bt||bt({ReactiveElement:mt}),(null!==(it=globalThis.reactiveElementVersions)&&void 0!==it?it:globalThis.reactiveElementVersions=[]).push("1.3.2");var yt=globalThis.trustedTypes,_t=yt?yt.createPolicy("lit-html",{createHTML:t=>t}):void 0,$t=`lit$${(Math.random()+"").slice(9)}$`,wt="?"+$t,At=`<${wt}>`,xt=document,Ct=(t="")=>xt.createComment(t),kt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,St=Array.isArray,Et=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Tt=/-->/g,Pt=/>/g,zt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,Ut=/'/g,Lt=/"/g,Ht=/^(?:script|style|textarea|title)$/i,Nt=t=>(e,...o)=>({_$litType$:t,strings:e,values:o}),Ot=Nt(1),Mt=Nt(2),Dt=Symbol.for("lit-noChange"),Rt=Symbol.for("lit-nothing"),Ft=new WeakMap,Bt=xt.createTreeWalker(xt,129,null,!1),It=class{constructor({strings:t,_$litType$:e},o){let s;this.parts=[];let i=0,r=0;const n=t.length-1,a=this.parts,[l,d]=((t,e)=>{const o=t.length-1,s=[];let i,r=2===e?"<svg>":"",n=Et;for(let e=0;e<o;e++){const o=t[e];let a,l,d=-1,c=0;for(;c<o.length&&(n.lastIndex=c,l=n.exec(o),null!==l);)c=n.lastIndex,n===Et?"!--"===l[1]?n=Tt:void 0!==l[1]?n=Pt:void 0!==l[2]?(Ht.test(l[2])&&(i=RegExp("</"+l[2],"g")),n=zt):void 0!==l[3]&&(n=zt):n===zt?">"===l[0]?(n=null!=i?i:Et,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?zt:'"'===l[3]?Lt:Ut):n===Lt||n===Ut?n=zt:n===Tt||n===Pt?n=Et:(n=zt,i=void 0);const h=n===zt&&t[e+1].startsWith("/>")?" ":"";r+=n===Et?o+At:d>=0?(s.push(a),o.slice(0,d)+"$lit$"+o.slice(d)+$t+h):o+$t+(-2===d?(s.push(void 0),e):h)}const a=r+(t[o]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==_t?_t.createHTML(a):a,s]})(t,e);if(this.el=It.createElement(l,o),Bt.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=Bt.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith($t)){const o=d[r++];if(t.push(e),void 0!==o){const t=s.getAttribute(o.toLowerCase()+"$lit$").split($t),e=/([.?@])?(.*)/.exec(o);a.push({type:1,index:i,name:e[2],strings:t,ctor:"."===e[1]?Yt:"?"===e[1]?Zt:"@"===e[1]?Jt:Kt})}else a.push({type:6,index:i})}for(const e of t)s.removeAttribute(e)}if(Ht.test(s.tagName)){const t=s.textContent.split($t),e=t.length-1;if(e>0){s.textContent=yt?yt.emptyScript:"";for(let o=0;o<e;o++)s.append(t[o],Ct()),Bt.nextNode(),a.push({type:2,index:++i});s.append(t[e],Ct())}}}else if(8===s.nodeType)if(s.data===wt)a.push({type:2,index:i});else{let t=-1;for(;-1!==(t=s.data.indexOf($t,t+1));)a.push({type:7,index:i}),t+=$t.length-1}i++}}static createElement(t,e){const o=xt.createElement("template");return o.innerHTML=t,o}};function jt(t,e,o=t,s){var i,r,n,a;if(e===Dt)return e;let l=void 0!==s?null===(i=o._$Cl)||void 0===i?void 0:i[s]:o._$Cu;const d=kt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,o,s)),void 0!==s?(null!==(n=(a=o)._$Cl)&&void 0!==n?n:a._$Cl=[])[s]=l:o._$Cu=l),void 0!==l&&(e=jt(t,l._$AS(t,e.values),l,s)),e}var Vt,Wt,qt=class{constructor(t,e,o,s){var i;this.type=2,this._$AH=Rt,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=o,this.options=s,this._$Cg=null===(i=null==s?void 0:s.isConnected)||void 0===i||i}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=jt(this,t,e),kt(t)?t===Rt||null==t||""===t?(this._$AH!==Rt&&this._$AR(),this._$AH=Rt):t!==this._$AH&&t!==Dt&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):(t=>{var e;return St(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==Rt&&kt(this._$AH)?this._$AA.nextSibling.data=t:this.k(xt.createTextNode(t)),this._$AH=t}T(t){var e;const{values:o,_$litType$:s}=t,i="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=It.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===i)this._$AH.m(o);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:o},parts:s}=this._$AD,i=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:xt).importNode(o,!0);Bt.currentNode=i;let r=Bt.nextNode(),n=0,a=0,l=s[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new qt(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new Gt(r,this,t)),this.v.push(e),l=s[++a]}n!==(null==l?void 0:l.index)&&(r=Bt.nextNode(),n++)}return i}m(t){let e=0;for(const o of this.v)void 0!==o&&(void 0!==o.strings?(o._$AI(t,o,e),e+=o.strings.length-2):o._$AI(t[e])),e++}}(i,this),e=t.p(this.options);t.m(o),this.k(e),this._$AH=t}}_$AC(t){let e=Ft.get(t.strings);return void 0===e&&Ft.set(t.strings,e=new It(t)),e}S(t){St(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let o,s=0;for(const i of t)s===e.length?e.push(o=new qt(this.M(Ct()),this.M(Ct()),this,this.options)):o=e[s],o._$AI(i),s++;s<e.length&&(this._$AR(o&&o._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var o;for(null===(o=this._$AP)||void 0===o||o.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Kt=class{constructor(t,e,o,s,i){this.type=1,this._$AH=Rt,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=i,o.length>2||""!==o[0]||""!==o[1]?(this._$AH=Array(o.length-1).fill(new String),this.strings=o):this._$AH=Rt}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,o,s){const i=this.strings;let r=!1;if(void 0===i)t=jt(this,t,e,0),r=!kt(t)||t!==this._$AH&&t!==Dt,r&&(this._$AH=t);else{const s=t;let n,a;for(t=i[0],n=0;n<i.length-1;n++)a=jt(this,s[o+n],e,n),a===Dt&&(a=this._$AH[n]),r||(r=!kt(a)||a!==this._$AH[n]),a===Rt?t=Rt:t!==Rt&&(t+=(null!=a?a:"")+i[n+1]),this._$AH[n]=a}r&&!s&&this.C(t)}C(t){t===Rt?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Yt=class extends Kt{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===Rt?void 0:t}},Xt=yt?yt.emptyScript:"",Zt=class extends Kt{constructor(){super(...arguments),this.type=4}C(t){t&&t!==Rt?this.element.setAttribute(this.name,Xt):this.element.removeAttribute(this.name)}},Jt=class extends Kt{constructor(t,e,o,s,i){super(t,e,o,s,i),this.type=5}_$AI(t,e=this){var o;if((t=null!==(o=jt(this,t,e,0))&&void 0!==o?o:Rt)===Dt)return;const s=this._$AH,i=t===Rt&&s!==Rt||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==Rt&&(s===Rt||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,o;"function"==typeof this._$AH?this._$AH.call(null!==(o=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==o?o:this.element,t):this._$AH.handleEvent(t)}},Gt=class{constructor(t,e,o){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=o}get _$AU(){return this._$AM._$AU}_$AI(t){jt(this,t)}},Qt=window.litHtmlPolyfillSupport;null==Qt||Qt(It,qt),(null!==(rt=globalThis.litHtmlVersions)&&void 0!==rt?rt:globalThis.litHtmlVersions=[]).push("2.2.4");var te=class extends mt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const o=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=o.firstChild),o}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,o)=>{var s,i;const r=null!==(s=null==o?void 0:o.renderBefore)&&void 0!==s?s:e;let n=r._$litPart$;if(void 0===n){const t=null!==(i=null==o?void 0:o.renderBefore)&&void 0!==i?i:null;r._$litPart$=n=new qt(e.insertBefore(Ct(),t),t,void 0,null!=o?o:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return Dt}};te.finalized=!0,te._$litElement$=!0,null===(Vt=globalThis.litElementHydrateSupport)||void 0===Vt||Vt.call(globalThis,{LitElement:te});var ee=globalThis.litElementPolyfillSupport;null==ee||ee({LitElement:te}),(null!==(Wt=globalThis.litElementVersions)&&void 0!==Wt?Wt:globalThis.litElementVersions=[]).push("3.2.0");var oe=ct`
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
`,se=ct`
  ${oe}

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
`,ie=(Object.create,Object.defineProperty),re=Object.defineProperties,ne=Object.getOwnPropertyDescriptor,ae=Object.getOwnPropertyDescriptors,le=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),de=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),ce=Object.prototype.propertyIsEnumerable,he=(t,e,o)=>e in t?ie(t,e,{enumerable:!0,configurable:!0,writable:!0,value:o}):t[e]=o,ue=(t,e)=>{for(var o in e||(e={}))de.call(e,o)&&he(t,o,e[o]);if(le)for(var o of le(e))ce.call(e,o)&&he(t,o,e[o]);return t},pe=(t,e)=>re(t,ae(e)),be=(t,e,o,s)=>{for(var i,r=s>1?void 0:s?ne(e,o):e,n=t.length-1;n>=0;n--)(i=t[n])&&(r=(s?i(e,o,r):i(r))||r);return s&&r&&ie(e,o,r),r};function ve(t,e){const o=ue({waitUntilFirstUpdate:!1},e);return(e,s)=>{const{update:i}=e;if(t in e){const r=t;e.update=function(t){if(t.has(r)){const e=t.get(r),i=this[r];e!==i&&(o.waitUntilFirstUpdate&&!this.hasUpdated||this[s](e,i))}i.call(this,t)}}}}var fe=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:o,elements:s}=e;return{kind:o,elements:s,finisher(e){window.customElements.define(t,e)}}})(t,e),ge=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?pe(ue({},e),{finisher(o){o.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(o){o.createProperty(e.key,t)}};function me(t){return(e,o)=>void 0!==o?((t,e,o)=>{e.constructor.createProperty(o,t)})(t,e,o):ge(t,e)}function ye(t){return me(pe(ue({},t),{state:!0}))}var _e;function $e(t,e){return(({finisher:t,descriptor:e})=>(o,s)=>{var i;if(void 0===s){const s=null!==(i=o.originalKey)&&void 0!==i?i:o.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(o.key)}:pe(ue({},o),{key:s});return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const i=o.constructor;void 0!==e&&Object.defineProperty(o,s,e(s)),null==t||t(i,s)}})({descriptor:o=>{const s={get(){var e,o;return null!==(o=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==o?o:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof o?Symbol():"__"+o;s.get=function(){var o,s;return void 0===this[e]&&(this[e]=null!==(s=null===(o=this.renderRoot)||void 0===o?void 0:o.querySelector(t))&&void 0!==s?s:null),this[e]}}return s}})}null===(_e=window.HTMLSlotElement)||void 0===_e||_e.prototype.assignedElements;var we=class extends te{constructor(){super(...arguments),this.vertical=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","separator")}handleVerticalChange(){this.setAttribute("aria-orientation",this.vertical?"vertical":"horizontal")}};function Ae(t){const e=t.tagName.toLowerCase();return"-1"!==t.getAttribute("tabindex")&&!t.hasAttribute("disabled")&&(!t.hasAttribute("aria-disabled")||"false"===t.getAttribute("aria-disabled"))&&!("input"===e&&"radio"===t.getAttribute("type")&&!t.hasAttribute("checked"))&&null!==t.offsetParent&&"hidden"!==window.getComputedStyle(t).visibility&&(!("audio"!==e&&"video"!==e||!t.hasAttribute("controls"))||!!t.hasAttribute("tabindex")||!(!t.hasAttribute("contenteditable")||"false"===t.getAttribute("contenteditable"))||["button","input","select","textarea","a","audio","video","summary"].includes(e))}we.styles=se,be([me({type:Boolean,reflect:!0})],we.prototype,"vertical",2),be([ve("vertical")],we.prototype,"handleVerticalChange",1),we=be([fe("sl-divider")],we);var xe=[],Ce=new Set;function ke(t){Ce.add(t),document.body.classList.add("sl-scroll-lock")}function Se(t){Ce.delete(t),0===Ce.size&&document.body.classList.remove("sl-scroll-lock")}function Ee(t,e,o="vertical",s="smooth"){const i=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=i.top+e.scrollTop,n=i.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,d=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==o&&"both"!==o||(n<a?e.scrollTo({left:n,behavior:s}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:s})),"vertical"!==o&&"both"!==o||(r<d?e.scrollTo({top:r,behavior:s}):r+t.clientHeight>c&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:s}))}var Te=ct`
  ${oe}

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
`;function Pe(t,e,o){return new Promise((s=>{if((null==o?void 0:o.duration)===1/0)throw new Error("Promise-based animations must be finite.");const i=t.animate(e,pe(ue({},o),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:o.duration}));i.addEventListener("cancel",s,{once:!0}),i.addEventListener("finish",s,{once:!0})}))}function ze(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const o=requestAnimationFrame(e);t.addEventListener("cancel",(()=>o),{once:!0}),t.addEventListener("finish",(()=>o),{once:!0}),t.cancel()})))))}function Ue(t,e){return t.map((t=>pe(ue({},t),{height:"auto"===t.height?`${e}px`:t.height})))}var Le=new Map,He=new WeakMap;function Ne(t,e){return"rtl"===e.toLowerCase()?{keyframes:t.rtlKeyframes||t.keyframes,options:t.options}:t}function Oe(t,e){Le.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function Me(t,e,o){const s=He.get(t);if(null==s?void 0:s[e])return Ne(s[e],o.dir);const i=Le.get(e);return i?Ne(i,o.dir):{keyframes:[],options:{duration:0}}}var De,Re=new Set,Fe=new MutationObserver(Ve),Be=new Map,Ie=document.documentElement.dir||"ltr",je=document.documentElement.lang||navigator.language;function Ve(){Ie=document.documentElement.dir||"ltr",je=document.documentElement.lang||navigator.language,[...Re.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}Fe.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]});var We=class extends class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Re.add(this.host)}hostDisconnected(){Re.delete(this.host)}dir(){return`${this.host.dir||Ie}`.toLowerCase()}lang(){return`${this.host.lang||je}`.toLowerCase()}term(t,...e){const o=this.lang().toLowerCase().slice(0,2),s=this.lang().length>2?this.lang().toLowerCase():"",i=Be.get(s),r=Be.get(o);let n;if(i&&i[t])n=i[t];else if(r&&r[t])n=r[t];else{if(!De||!De[t])return console.error(`No translation found for: ${String(t)}`),t;n=De[t]}return"function"==typeof n?n(...e):n}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,o){return new Intl.RelativeTimeFormat(this.lang(),o).format(t,e)}}{};!function(...t){t.map((t=>{const e=t.$code.toLowerCase();Be.has(e)?Be.set(e,Object.assign(Object.assign({},Be.get(e)),t)):Be.set(e,t),De||(De=t)})),Ve()}({$code:"en",$name:"English",$dir:"ltr",clearEntry:"Clear entry",close:"Close",copy:"Copy",currentValue:"Current value",hidePassword:"Hide password",loading:"Loading",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",toggleColorFormat:"Toggle color format"});var qe=class{constructor(t,...e){this.slotNames=[],(this.host=t).addController(this),this.slotNames=e,this.handleSlotChange=this.handleSlotChange.bind(this)}hasDefaultSlot(){return[...this.host.childNodes].some((t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1}))}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}handleSlotChange(t){const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()}},Ke=t=>(...e)=>({_$litDirective$:t,values:e}),Ye=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,o){this._$Ct=t,this._$AM=e,this._$Ci=o}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},Xe=Ke(class extends Ye{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var o,s;if(void 0===this.et){this.et=new Set,void 0!==t.strings&&(this.st=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(o=this.st)||void 0===o?void 0:o.has(t))&&this.et.add(t);return this.render(e)}const i=t.element.classList;this.et.forEach((t=>{t in e||(i.remove(t),this.et.delete(t))}));for(const t in e){const o=!!e[t];o===this.et.has(t)||(null===(s=this.st)||void 0===s?void 0:s.has(t))||(o?(i.add(t),this.et.add(t)):(i.remove(t),this.et.delete(t)))}return Dt}}),Ze=t=>null!=t?t:Rt;function Je(t,e,o){const s=new CustomEvent(e,ue({bubbles:!0,cancelable:!1,composed:!0,detail:{}},o));return t.dispatchEvent(s),s}function Ge(t,e){return new Promise((o=>{t.addEventListener(e,(function s(i){i.target===t&&(t.removeEventListener(e,s),o())}))}))}var Qe=class extends te{constructor(){super(...arguments),this.hasSlotController=new qe(this,"footer"),this.localize=new We(this),this.open=!1,this.label="",this.noHeader=!1}connectedCallback(){super.connectedCallback(),this.modal=new class{constructor(t){this.tabDirection="forward",this.element=t,this.handleFocusIn=this.handleFocusIn.bind(this),this.handleKeyDown=this.handleKeyDown.bind(this),this.handleKeyUp=this.handleKeyUp.bind(this)}activate(){xe.push(this.element),document.addEventListener("focusin",this.handleFocusIn),document.addEventListener("keydown",this.handleKeyDown),document.addEventListener("keyup",this.handleKeyUp)}deactivate(){xe=xe.filter((t=>t!==this.element)),document.removeEventListener("focusin",this.handleFocusIn),document.removeEventListener("keydown",this.handleKeyDown),document.removeEventListener("keyup",this.handleKeyUp)}isActive(){return xe[xe.length-1]===this.element}checkFocus(){if(this.isActive()&&!this.element.matches(":focus-within")){const{start:t,end:e}=function(t){var e,o;const s=[];return function t(e){e instanceof HTMLElement&&(s.push(e),null!==e.shadowRoot&&"open"===e.shadowRoot.mode&&t(e.shadowRoot)),[...e.children].forEach((e=>t(e)))}(t),{start:null!=(e=s.find((t=>Ae(t))))?e:null,end:null!=(o=s.reverse().find((t=>Ae(t))))?o:null}}(this.element),o="forward"===this.tabDirection?t:e;"function"==typeof(null==o?void 0:o.focus)&&o.focus({preventScroll:!0})}}handleFocusIn(){this.checkFocus()}handleKeyDown(t){"Tab"===t.key&&t.shiftKey&&(this.tabDirection="backward"),requestAnimationFrame((()=>this.checkFocus()))}handleKeyUp(){this.tabDirection="forward"}}(this)}firstUpdated(){this.dialog.hidden=!this.open,this.open&&(this.modal.activate(),ke(this))}disconnectedCallback(){super.disconnectedCallback(),Se(this)}async show(){if(!this.open)return this.open=!0,Ge(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Ge(this,"sl-after-hide")}requestClose(t){if(Je(this,"sl-request-close",{cancelable:!0,detail:{source:t}}).defaultPrevented){const t=Me(this,"dialog.denyClose",{dir:this.localize.dir()});Pe(this.panel,t.keyframes,t.options)}else this.hide()}handleKeyDown(t){"Escape"===t.key&&(t.stopPropagation(),this.requestClose("keyboard"))}async handleOpenChange(){if(this.open){Je(this,"sl-show"),this.originalTrigger=document.activeElement,this.modal.activate(),ke(this);const t=this.querySelector("[autofocus]");t&&t.removeAttribute("autofocus"),await Promise.all([ze(this.dialog),ze(this.overlay)]),this.dialog.hidden=!1,requestAnimationFrame((()=>{Je(this,"sl-initial-focus",{cancelable:!0}).defaultPrevented||(t?t.focus({preventScroll:!0}):this.panel.focus({preventScroll:!0})),t&&t.setAttribute("autofocus","")}));const e=Me(this,"dialog.show",{dir:this.localize.dir()}),o=Me(this,"dialog.overlay.show",{dir:this.localize.dir()});await Promise.all([Pe(this.panel,e.keyframes,e.options),Pe(this.overlay,o.keyframes,o.options)]),Je(this,"sl-after-show")}else{Je(this,"sl-hide"),this.modal.deactivate(),await Promise.all([ze(this.dialog),ze(this.overlay)]);const t=Me(this,"dialog.hide",{dir:this.localize.dir()}),e=Me(this,"dialog.overlay.hide",{dir:this.localize.dir()});await Promise.all([Pe(this.panel,t.keyframes,t.options),Pe(this.overlay,e.keyframes,e.options)]),this.dialog.hidden=!0,Se(this);const o=this.originalTrigger;"function"==typeof(null==o?void 0:o.focus)&&setTimeout((()=>o.focus())),Je(this,"sl-after-hide")}}render(){return Ot`
      <div
        part="base"
        class=${Xe({dialog:!0,"dialog--open":this.open,"dialog--has-footer":this.hasSlotController.test("footer")})}
        @keydown=${this.handleKeyDown}
      >
        <div part="overlay" class="dialog__overlay" @click=${()=>this.requestClose("overlay")} tabindex="-1"></div>

        <div
          part="panel"
          class="dialog__panel"
          role="dialog"
          aria-modal="true"
          aria-hidden=${this.open?"false":"true"}
          aria-label=${Ze(this.noHeader?this.label:void 0)}
          aria-labelledby=${Ze(this.noHeader?void 0:"title")}
          tabindex="0"
        >
          ${this.noHeader?"":Ot`
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
    `}};Qe.styles=Te,be([$e(".dialog")],Qe.prototype,"dialog",2),be([$e(".dialog__panel")],Qe.prototype,"panel",2),be([$e(".dialog__overlay")],Qe.prototype,"overlay",2),be([me({type:Boolean,reflect:!0})],Qe.prototype,"open",2),be([me({reflect:!0})],Qe.prototype,"label",2),be([me({attribute:"no-header",type:Boolean,reflect:!0})],Qe.prototype,"noHeader",2),be([ve("open",{waitUntilFirstUpdate:!0})],Qe.prototype,"handleOpenChange",1),Qe=be([fe("sl-dialog")],Qe),Oe("dialog.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),Oe("dialog.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}}),Oe("dialog.denyClose",{keyframes:[{transform:"scale(1)"},{transform:"scale(1.02)"},{transform:"scale(1)"}],options:{duration:250}}),Oe("dialog.overlay.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:250}}),Oe("dialog.overlay.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:250}});var to=ct`
  ${oe}

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
`,eo=Symbol.for(""),oo=t=>{var e,o;if((null===(e=t)||void 0===e?void 0:e.r)===eo)return null===(o=t)||void 0===o?void 0:o._$litStatic$},so=(t,...e)=>({_$litStatic$:e.reduce(((e,o,s)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(o)+t[s+1]),t[0]),r:eo}),io=new Map,ro=t=>(e,...o)=>{const s=o.length;let i,r;const n=[],a=[];let l,d=0,c=!1;for(;d<s;){for(l=e[d];d<s&&void 0!==(r=o[d],i=oo(r));)l+=i+e[++d],c=!0;a.push(r),n.push(l),d++}if(d===s&&n.push(e[s]),c){const t=n.join("$$lit$$");void 0===(e=io.get(t))&&(n.raw=n,io.set(t,e=n)),o=a}return t(e,...o)},no=ro(Ot),ao=(ro(Mt),class extends te{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Je(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Je(this,"sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}render(){const t=!!this.href,e=t?so`a`:so`button`;return no`
      <${e}
        part="base"
        class=${Xe({"icon-button":!0,"icon-button--disabled":!t&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${Ze(t?void 0:this.disabled)}
        type=${Ze(t?void 0:"button")}
        href=${Ze(t?this.href:void 0)}
        target=${Ze(t?this.target:void 0)}
        download=${Ze(t?this.download:void 0)}
        rel=${Ze(t&&this.target?"noreferrer noopener":void 0)}
        role=${Ze(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          class="icon-button__icon"
          name=${Ze(this.name)}
          library=${Ze(this.library)}
          src=${Ze(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${e}>
    `}});ao.styles=to,be([ye()],ao.prototype,"hasFocus",2),be([$e(".icon-button")],ao.prototype,"button",2),be([me()],ao.prototype,"name",2),be([me()],ao.prototype,"library",2),be([me()],ao.prototype,"src",2),be([me()],ao.prototype,"href",2),be([me()],ao.prototype,"target",2),be([me()],ao.prototype,"download",2),be([me()],ao.prototype,"label",2),be([me({type:Boolean,reflect:!0})],ao.prototype,"disabled",2),ao=be([fe("sl-icon-button")],ao);var lo="";function co(t){lo=t}var ho={name:"default",resolver:t=>`${function(){if(!lo){const t=[...document.getElementsByTagName("script")],e=t.find((t=>t.hasAttribute("data-shoelace")));if(e)co(e.getAttribute("data-shoelace"));else{const e=t.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let o="";e&&(o=e.getAttribute("src")),co(o.split("/").slice(0,-1).join("/"))}}return lo.replace(/\/$/,"")}()}/assets/icons/${t}.svg`},uo={"check-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">\n      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"></path>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},po=[ho,{name:"system",resolver:t=>t in uo?`data:image/svg+xml,${encodeURIComponent(uo[t])}`:""}],bo=[];function vo(t){return po.find((e=>e.name===t))}var fo=new Map,go=new Map;var mo=ct`
  ${oe}

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
`,yo=class extends Ye{constructor(t){if(super(t),this.it=Rt,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===Rt||null==t)return this.ft=void 0,this.it=t;if(t===Dt)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.ft;this.it=t;const e=[t];return e.raw=e,this.ft={_$litType$:this.constructor.resultType,strings:e,values:[]}}};yo.directiveName="unsafeHTML",yo.resultType=1,Ke(yo);var _o=class extends yo{};_o.directiveName="unsafeSVG",_o.resultType=2;var $o,wo=Ke(_o),Ao=class extends te{constructor(){super(...arguments),this.svg="",this.label="",this.library="default"}connectedCallback(){super.connectedCallback(),bo.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,bo=bo.filter((e=>e!==t))}getUrl(){const t=vo(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){var t;const e=vo(this.library),o=this.getUrl();if($o||($o=new DOMParser),o)try{const s=await async function(t){if(go.has(t))return go.get(t);const e=await function(t,e="cors"){if(fo.has(t))return fo.get(t);const o=fetch(t,{mode:e}).then((async t=>({ok:t.ok,status:t.status,html:await t.text()})));return fo.set(t,o),o}(t),o={ok:e.ok,status:e.status,svg:null};if(e.ok){const t=document.createElement("div");t.innerHTML=e.html;const s=t.firstElementChild;o.svg="svg"===(null==s?void 0:s.tagName.toLowerCase())?s.outerHTML:""}return go.set(t,o),o}(o);if(o!==this.getUrl())return;if(s.ok){const o=$o.parseFromString(s.svg,"text/html").body.querySelector("svg");null!==o?(null==(t=null==e?void 0:e.mutator)||t.call(e,o),this.svg=o.outerHTML,Je(this,"sl-load")):(this.svg="",Je(this,"sl-error"))}else this.svg="",Je(this,"sl-error")}catch(t){Je(this,"sl-error")}else this.svg.length>0&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return Ot` <div
      part="base"
      class="icon"
      role=${Ze(t?"img":void 0)}
      aria-label=${Ze(t?this.label:void 0)}
      aria-hidden=${Ze(t?void 0:"true")}
    >
      ${wo(this.svg)}
    </div>`}};Ao.styles=mo,be([ye()],Ao.prototype,"svg",2),be([me({reflect:!0})],Ao.prototype,"name",2),be([me()],Ao.prototype,"src",2),be([me()],Ao.prototype,"label",2),be([me({reflect:!0})],Ao.prototype,"library",2),be([ve("name"),ve("src"),ve("library")],Ao.prototype,"setIcon",1),Ao=be([fe("sl-icon")],Ao);const{H:xo}=G,Co=t=>(...e)=>({_$litDirective$:t,values:e}),ko=(t,e)=>{var o,s;const i=t._$AN;if(void 0===i)return!1;for(const t of i)null===(s=(o=t)._$AO)||void 0===s||s.call(o,e,!1),ko(t,e);return!0},So=t=>{let e,o;do{if(void 0===(e=t._$AM))break;o=e._$AN,o.delete(t),t=e}while(0===(null==o?void 0:o.size))},Eo=t=>{for(let e;e=t._$AM;t=e){let o=e._$AN;if(void 0===o)e._$AN=o=new Set;else if(o.has(t))break;o.add(t),zo(e)}};function To(t){void 0!==this._$AN?(So(this),this._$AM=t,Eo(this)):this._$AM=t}function Po(t,e=!1,o=0){const s=this._$AH,i=this._$AN;if(void 0!==i&&0!==i.size)if(e)if(Array.isArray(s))for(let t=o;t<s.length;t++)ko(s[t],!1),So(s[t]);else null!=s&&(ko(s,!1),So(s));else ko(this,t)}const zo=t=>{var e,o,s,i;2==t.type&&(null!==(e=(s=t)._$AP)&&void 0!==e||(s._$AP=Po),null!==(o=(i=t)._$AQ)&&void 0!==o||(i._$AQ=To))};class Uo extends class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,o){this._$Ct=t,this._$AM=e,this._$Ci=o}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,o){super._$AT(t,e,o),Eo(this),this.isConnected=t._$AU}_$AO(t,e=!0){var o,s;t!==this.isConnected&&(this.isConnected=t,t?null===(o=this.reconnected)||void 0===o||o.call(this):null===(s=this.disconnected)||void 0===s||s.call(this)),e&&(ko(this,t),So(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Lo{constructor(t){this.Y=t}disconnect(){this.Y=void 0}reconnect(t){this.Y=t}deref(){return this.Y}}class Ho{constructor(){this.Z=void 0,this.q=void 0}get(){return this.Z}pause(){var t;null!==(t=this.Z)&&void 0!==t||(this.Z=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Z=this.q=void 0}}const No=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,Oo=Co(class extends Uo{constructor(){super(...arguments),this._$Cwt=1073741823,this._$Cyt=[],this._$CK=new Lo(this),this._$CX=new Ho}render(...t){var e;return null!==(e=t.find((t=>!No(t))))&&void 0!==e?e:M}update(t,e){const o=this._$Cyt;let s=o.length;this._$Cyt=e;const i=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cwt);t++){const n=e[t];if(!No(n))return this._$Cwt=t,n;t<s&&n===o[t]||(this._$Cwt=1073741823,s=0,Promise.resolve(n).then((async t=>{for(;r.get();)await r.get();const e=i.deref();if(void 0!==e){const o=e._$Cyt.indexOf(n);o>-1&&o<e._$Cwt&&(e._$Cwt=o,e.setValue(t))}})))}return M}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}});class Mo{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class Do extends ot{static properties={file:{type:File},template:{attribute:!1}};static styles=r`
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
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),o=t.stream().getReader();let{value:s,done:i}=await o.read();s=s?e.decode(s,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(s);if(t)yield s.substring(n,t.index),n=r.lastIndex;else{if(i)break;const t=s.substr(n);({value:s,done:i}=await o.read()),s=t+(s?e.decode(s,{stream:!0}):""),n=r.lastIndex=0}}n<s.length&&(yield s.substr(n))}render(){if(!this.file)return O``;const t=this.parseSrc();return O`${Oo(t,O``)}`}}customElements.define("sc-report-table",Do),customElements.define("sc-intro-tbl",class extends Do{parseHeader(t){const e=t.split(";");return O`
            <tr>
                ${e.map((t=>O`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=O``,o=!0;for(const s of t.split(";")){const[t,i,r]=s.split("|");let n=O`${t}`;r&&(n=O`<a href=${r}>${n}</a>`),i&&(n=O`<abbr title=${i}>${n}</abbr>`),o?(e=O`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,o=!1):e=O`${e}
                    <td>
                        ${n}
                    </td>
                `}return O`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.file);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Mo("first line in intro table file should be a header.");e=e.slice(2);let o=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Mo("lines following the first should all be normal table rows.");e=e.slice(2),o=O`${o}${this.parseRow(e)}`}return O`<table>${o}</table>`}});var Ro=ct`
  ${oe}

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
`,Fo=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Bo=class extends te{constructor(){super(...arguments),this.hasSlotController=new qe(this,"icon","suffix"),this.localize=new We(this),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,Ge(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Ge(this,"sl-after-hide")}async toast(){return new Promise((t=>{null===Fo.parentElement&&document.body.append(Fo),Fo.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{Fo.removeChild(this),t(),null===Fo.querySelector("sl-alert")&&Fo.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){Je(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await ze(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=Me(this,"alert.show",{dir:this.localize.dir()});await Pe(this.base,t,e),Je(this,"sl-after-show")}else{Je(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await ze(this.base);const{keyframes:t,options:e}=Me(this,"alert.hide",{dir:this.localize.dir()});await Pe(this.base,t,e),this.base.hidden=!0,Je(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return Ot`
      <div
        part="base"
        class=${Xe({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--has-icon":this.hasSlotController.test("icon"),"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
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

        ${this.closable?Ot`
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
    `}};Bo.styles=Ro,be([$e('[part="base"]')],Bo.prototype,"base",2),be([me({type:Boolean,reflect:!0})],Bo.prototype,"open",2),be([me({type:Boolean,reflect:!0})],Bo.prototype,"closable",2),be([me({reflect:!0})],Bo.prototype,"variant",2),be([me({type:Number})],Bo.prototype,"duration",2),be([ve("open",{waitUntilFirstUpdate:!0})],Bo.prototype,"handleOpenChange",1),be([ve("duration")],Bo.prototype,"handleDurationChange",1),Bo=be([fe("sl-alert")],Bo),Oe("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),Oe("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var Io=ct`
  ${oe}

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
`,jo=class extends te{constructor(){super(...arguments),this.localize=new We(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{var o;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(o=this.getActiveTab())?o:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t={includeDisabled:!0}){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t.includeDisabled?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement,o="rtl"===this.localize.dir();if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&t.key===(o?"ArrowRight":"ArrowLeft")||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s--:(["top","bottom"].includes(this.placement)&&t.key===(o?"ArrowLeft":"ArrowRight")||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&s++,s<0&&(s=this.tabs.length-1),s>this.tabs.length-1&&(s=0),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Ee(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft+this.nav.clientWidth:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft-this.nav.clientWidth:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth}setActiveTab(t,e){if(e=ue({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const o=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)})),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Ee(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(o&&Je(this,"sl-tab-hide",{detail:{name:o.panel}}),Je(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,o=t.clientHeight,s="rtl"===this.localize.dir(),i=this.getAllTabs(),r=i.slice(0,i.indexOf(t)).reduce(((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight})),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=s?`translateX(${-1*r.left}px)`:`translateX(${r.left}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${o}px`,this.indicator.style.transform=`translateY(${r.top}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs({includeDisabled:!1}),this.panels=this.getAllPanels(),this.syncIndicator()}render(){const t="rtl"===this.localize.dir();return Ot`
      <div
        part="base"
        class=${Xe({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--rtl":"rtl"===this.localize.dir(),"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?Ot`
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

          ${this.hasScrollControls?Ot`
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
    `}};jo.styles=Io,be([$e(".tab-group")],jo.prototype,"tabGroup",2),be([$e(".tab-group__body")],jo.prototype,"body",2),be([$e(".tab-group__nav")],jo.prototype,"nav",2),be([$e(".tab-group__indicator")],jo.prototype,"indicator",2),be([ye()],jo.prototype,"hasScrollControls",2),be([me()],jo.prototype,"placement",2),be([me()],jo.prototype,"activation",2),be([me({attribute:"no-scroll-controls",type:Boolean})],jo.prototype,"noScrollControls",2),be([me()],jo.prototype,"lang",2),be([ve("noScrollControls",{waitUntilFirstUpdate:!0})],jo.prototype,"updateScrollControls",1),be([ve("placement",{waitUntilFirstUpdate:!0})],jo.prototype,"syncIndicator",1),jo=be([fe("sl-tab-group")],jo);var Vo=0;function Wo(){return++Vo}var qo=ct`
  ${oe}

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
`,Ko=class extends te{constructor(){super(...arguments),this.localize=new We(this),this.attrId=Wo(),this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","tab")}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Je(this,"sl-close")}handleActiveChange(){this.setAttribute("aria-selected",this.active?"true":"false")}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false")}render(){return this.id=this.id.length>0?this.id:this.componentId,Ot`
      <div
        part="base"
        class=${Xe({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        tabindex="0"
      >
        <slot></slot>
        ${this.closable?Ot`
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
    `}};Ko.styles=qo,be([$e(".tab")],Ko.prototype,"tab",2),be([me({reflect:!0})],Ko.prototype,"panel",2),be([me({type:Boolean,reflect:!0})],Ko.prototype,"active",2),be([me({type:Boolean})],Ko.prototype,"closable",2),be([me({type:Boolean,reflect:!0})],Ko.prototype,"disabled",2),be([me()],Ko.prototype,"lang",2),be([ve("active")],Ko.prototype,"handleActiveChange",1),be([ve("disabled")],Ko.prototype,"handleDisabledChange",1),Ko=be([fe("sl-tab")],Ko);var Yo=ct`
  ${oe}

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
`,Xo=class extends te{constructor(){super(...arguments),this.attrId=Wo(),this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId,this.setAttribute("role","tabpanel")}handleActiveChange(){this.setAttribute("aria-hidden",this.active?"false":"true")}render(){return Ot`
      <div
        part="base"
        class=${Xe({"tab-panel":!0,"tab-panel--active":this.active})}
      >
        <slot></slot>
      </div>
    `}};Xo.styles=Yo,be([me({reflect:!0})],Xo.prototype,"name",2),be([me({type:Boolean,reflect:!0})],Xo.prototype,"active",2),be([ve("active")],Xo.prototype,"handleActiveChange",1),Xo=be([fe("sl-tab-panel")],Xo);class Zo extends ot{visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return this.visibleTemplate()}}customElements.define("sc-tab",Zo);var Jo=ct`
  ${oe}

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
`,Go=class extends te{constructor(){super(...arguments),this.localize=new We(this)}render(){return Ot`
      <svg part="base" class="spinner" role="progressbar" aria-valuetext=${this.localize.term("loading")}>
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};Go.styles=Jo,Go=be([fe("sl-spinner")],Go);class Qo extends ot{static styles=r`
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
  `;static properties={path:{type:String},_visible:{type:Boolean,state:!0}};connectedCallback(){super.connectedCallback(),this.observer=new IntersectionObserver(((t,e)=>{t.forEach((t=>{t.isIntersecting?this._visible=!0:this._visible=!1}))})),this.observer.observe(this.parentElement)}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}constructor(){super(),this._visible=!1}hideLoading(){this.renderRoot.querySelector("#loading").style.display="none"}render(){return this._visible?O`
                <div id="loading" class="loading">
                    <sl-spinner></sl-spinner>
                </div>
                <div class="plot">
                    <iframe @load=${this.hideLoading} seamless frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
                </div>
            `:O``}}customElements.define("sc-diagram",Qo);var ts=class extends Event{constructor(t){super("formdata"),this.formData=t}},es=class extends FormData{constructor(t){var e=(...t)=>{super(...t)};t?(e(t),this.form=t,t.dispatchEvent(new ts(this))):e()}append(t,e){if(!this.form)return super.append(t,e);let o=this.form.elements[t];if(o||(o=document.createElement("input"),o.type="hidden",o.name=t,this.form.appendChild(o)),this.has(t)){const s=this.getAll(t),i=s.indexOf(o.value);-1!==i&&s.splice(i,1),s.push(e),this.set(t,s)}else super.append(t,e);o.value=e}};function os(){window.FormData&&!function(){const t=document.createElement("form");let e=!1;return document.body.append(t),t.addEventListener("submit",(t=>{new FormData(t.target),t.preventDefault()})),t.addEventListener("formdata",(()=>e=!0)),t.dispatchEvent(new Event("submit",{cancelable:!0})),t.remove(),e}()&&(window.FormData=es,window.addEventListener("submit",(t=>{t.defaultPrevented||new FormData(t.target)})))}"complete"===document.readyState?os():window.addEventListener("DOMContentLoaded",(()=>os()));var ss=new WeakMap,is=ct`
  ${oe}

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
`,rs=class extends te{constructor(){super(...arguments),this.formSubmitController=new class{constructor(t,e){(this.host=t).addController(this),this.options=ue({form:t=>t.closest("form"),name:t=>t.name,value:t=>t.value,defaultValue:t=>t.defaultValue,disabled:t=>t.disabled,reportValidity:t=>"function"!=typeof t.reportValidity||t.reportValidity(),setValue:(t,e)=>{t.value=e}},e),this.handleFormData=this.handleFormData.bind(this),this.handleFormSubmit=this.handleFormSubmit.bind(this),this.handleFormReset=this.handleFormReset.bind(this),this.reportFormValidity=this.reportFormValidity.bind(this)}hostConnected(){this.form=this.options.form(this.host),this.form&&(this.form.addEventListener("formdata",this.handleFormData),this.form.addEventListener("submit",this.handleFormSubmit),this.form.addEventListener("reset",this.handleFormReset),ss.has(this.form)||(ss.set(this.form,this.form.reportValidity),this.form.reportValidity=()=>this.reportFormValidity()))}hostDisconnected(){this.form&&(this.form.removeEventListener("formdata",this.handleFormData),this.form.removeEventListener("submit",this.handleFormSubmit),this.form.removeEventListener("reset",this.handleFormReset),ss.has(this.form)&&(this.form.reportValidity=ss.get(this.form),ss.delete(this.form)),this.form=void 0)}handleFormData(t){const e=this.options.disabled(this.host),o=this.options.name(this.host),s=this.options.value(this.host);e||"string"!=typeof o||void 0===s||(Array.isArray(s)?s.forEach((e=>{t.formData.append(o,e.toString())})):t.formData.append(o,s.toString()))}handleFormSubmit(t){const e=this.options.disabled(this.host),o=this.options.reportValidity;!this.form||this.form.noValidate||e||o(this.host)||(t.preventDefault(),t.stopImmediatePropagation())}handleFormReset(){this.options.setValue(this.host,this.options.defaultValue(this.host))}reportFormValidity(){if(this.form&&!this.form.noValidate){const t=this.form.querySelectorAll("*");for(const e of t)if("function"==typeof e.reportValidity&&!e.reportValidity())return!1}return!0}doAction(t,e){if(this.form){const o=document.createElement("button");o.type=t,o.style.position="absolute",o.style.width="0",o.style.height="0",o.style.clipPath="inset(50%)",o.style.overflow="hidden",o.style.whiteSpace="nowrap",e&&["formaction","formmethod","formnovalidate","formtarget"].forEach((t=>{e.hasAttribute(t)&&o.setAttribute(t,e.getAttribute(t))})),this.form.append(o),o.click(),o.remove()}}reset(t){this.doAction("reset",t)}submit(t){this.doAction("submit",t)}}(this,{form:t=>{if(t.hasAttribute("form")){const e=t.getRootNode(),o=t.getAttribute("form");return e.getElementById(o)}return t.closest("form")}}),this.hasSlotController=new qe(this,"[default]","prefix","suffix"),this.localize=new We(this),this.hasFocus=!1,this.variant="default",this.size="medium",this.caret=!1,this.disabled=!1,this.loading=!1,this.outline=!1,this.pill=!1,this.circle=!1,this.type="button"}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}handleBlur(){this.hasFocus=!1,Je(this,"sl-blur")}handleFocus(){this.hasFocus=!0,Je(this,"sl-focus")}handleClick(t){if(this.disabled||this.loading)return t.preventDefault(),void t.stopPropagation();"submit"===this.type&&this.formSubmitController.submit(this),"reset"===this.type&&this.formSubmitController.reset(this)}render(){const t=!!this.href,e=t?so`a`:so`button`;return no`
      <${e}
        part="base"
        class=${Xe({button:!0,"button--default":"default"===this.variant,"button--primary":"primary"===this.variant,"button--success":"success"===this.variant,"button--neutral":"neutral"===this.variant,"button--warning":"warning"===this.variant,"button--danger":"danger"===this.variant,"button--text":"text"===this.variant,"button--small":"small"===this.size,"button--medium":"medium"===this.size,"button--large":"large"===this.size,"button--caret":this.caret,"button--circle":this.circle,"button--disabled":this.disabled,"button--focused":this.hasFocus,"button--loading":this.loading,"button--standard":!this.outline,"button--outline":this.outline,"button--pill":this.pill,"button--rtl":"rtl"===this.localize.dir(),"button--has-label":this.hasSlotController.test("[default]"),"button--has-prefix":this.hasSlotController.test("prefix"),"button--has-suffix":this.hasSlotController.test("suffix")})}
        ?disabled=${Ze(t?void 0:this.disabled)}
        type=${Ze(t?void 0:this.type)}
        name=${Ze(t?void 0:this.name)}
        value=${Ze(t?void 0:this.value)}
        href=${Ze(t?this.href:void 0)}
        target=${Ze(t?this.target:void 0)}
        download=${Ze(t?this.download:void 0)}
        rel=${Ze(t&&this.target?"noreferrer noopener":void 0)}
        role=${Ze(t?void 0:"button")}
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
        ${this.caret?no`
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
        ${this.loading?no`<sl-spinner></sl-spinner>`:""}
      </${e}>
    `}};rs.styles=is,be([$e(".button")],rs.prototype,"button",2),be([ye()],rs.prototype,"hasFocus",2),be([me({reflect:!0})],rs.prototype,"variant",2),be([me({reflect:!0})],rs.prototype,"size",2),be([me({type:Boolean,reflect:!0})],rs.prototype,"caret",2),be([me({type:Boolean,reflect:!0})],rs.prototype,"disabled",2),be([me({type:Boolean,reflect:!0})],rs.prototype,"loading",2),be([me({type:Boolean,reflect:!0})],rs.prototype,"outline",2),be([me({type:Boolean,reflect:!0})],rs.prototype,"pill",2),be([me({type:Boolean,reflect:!0})],rs.prototype,"circle",2),be([me()],rs.prototype,"type",2),be([me()],rs.prototype,"name",2),be([me()],rs.prototype,"value",2),be([me()],rs.prototype,"href",2),be([me()],rs.prototype,"target",2),be([me()],rs.prototype,"download",2),be([me()],rs.prototype,"form",2),be([me({attribute:"formaction"})],rs.prototype,"formAction",2),be([me({attribute:"formmethod"})],rs.prototype,"formMethod",2),be([me({attribute:"formnovalidate",type:Boolean})],rs.prototype,"formNoValidate",2),be([me({attribute:"formtarget"})],rs.prototype,"formTarget",2),rs=be([fe("sl-button")],rs);var ns=ct`
  ${oe}

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
`,as=class extends te{constructor(){super(...arguments),this.localize=new We(this),this.open=!1,this.disabled=!1}firstUpdated(){this.body.hidden=!this.open,this.body.style.height=this.open?"auto":"0"}async show(){if(!this.open&&!this.disabled)return this.open=!0,Ge(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,Ge(this,"sl-after-hide")}handleSummaryClick(){this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){Je(this,"sl-show"),await ze(this.body),this.body.hidden=!1;const{keyframes:t,options:e}=Me(this,"details.show",{dir:this.localize.dir()});await Pe(this.body,Ue(t,this.body.scrollHeight),e),this.body.style.height="auto",Je(this,"sl-after-show")}else{Je(this,"sl-hide"),await ze(this.body);const{keyframes:t,options:e}=Me(this,"details.hide",{dir:this.localize.dir()});await Pe(this.body,Ue(t,this.body.scrollHeight),e),this.body.hidden=!0,this.body.style.height="auto",Je(this,"sl-after-hide")}}render(){return Ot`
      <div
        part="base"
        class=${Xe({details:!0,"details--open":this.open,"details--disabled":this.disabled})}
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
    `}};as.styles=ns,be([$e(".details")],as.prototype,"details",2),be([$e(".details__header")],as.prototype,"header",2),be([$e(".details__body")],as.prototype,"body",2),be([me({type:Boolean,reflect:!0})],as.prototype,"open",2),be([me()],as.prototype,"summary",2),be([me({type:Boolean,reflect:!0})],as.prototype,"disabled",2),be([ve("open",{waitUntilFirstUpdate:!0})],as.prototype,"handleOpenChange",1),as=be([fe("sl-details")],as),Oe("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),Oe("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}});class ls extends ot{static styles=r`
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
    `;static properties={title:{type:String},paths:{type:Object},diff:{type:String}};getFileContents(t){return new Promise((function(e,o){fetch(t).then((t=>{if(!t.ok)throw new Error(`HTTP error: status ${t.status}`);return t.blob()})).then((t=>t.text())).then((t=>{e(t)}))}))}getNewTabBtnTemplate(t){return O`
            <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${t} target="_blank">
                Open in New Tab
            </sl-button>
        `}getDiffTemplate(){if(this.diff){const t=`${this.title}-diff`;return O`
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
            `}return O``}getTabTemplate(t,e){const o=`details-panel-${this.title}-${t}`;return O`
            <sl-tab class="tab" slot="nav" panel=${o}>${t}</sl-tab>
            <sl-tab-panel class="tab-panel" name=${o}>
                <div class="text-field-container">
                    <div>
                        ${this.getNewTabBtnTemplate(e)}
                    </div>
                    <pre><code>${Oo(this.getFileContents(e),O`Loading...`)}</code></pre>
                </div>
            </sl-tab-panel>
        `}render(){return O`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.paths).map((t=>this.getTabTemplate(t[0],t[1])))}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `}}customElements.define("sc-file-preview",ls);class ds{}const cs=new WeakMap,hs=Co(class extends Uo{render(t){return D}update(t,[e]){var o;const s=e!==this.Y;return s&&void 0!==this.Y&&this.rt(void 0),(s||this.lt!==this.dt)&&(this.Y=e,this.ct=null===(o=t.options)||void 0===o?void 0:o.host,this.rt(this.dt=t.element)),D}rt(t){var e;if("function"==typeof this.Y){const o=null!==(e=this.ct)&&void 0!==e?e:globalThis;let s=cs.get(o);void 0===s&&(s=new WeakMap,cs.set(o,s)),void 0!==s.get(this.Y)&&this.Y.call(this.ct,void 0),s.set(this.Y,t),void 0!==t&&this.Y.call(this.ct,t)}else this.Y.value=t}get lt(){var t,e,o;return"function"==typeof this.Y?null===(e=cs.get(null!==(t=this.ct)&&void 0!==t?t:globalThis))||void 0===e?void 0:e.get(this.Y):null===(o=this.Y)||void 0===o?void 0:o.value}disconnected(){this.lt===this.dt&&this.rt(void 0)}reconnected(){this.rt(this.dt)}});class us extends Do{static styles=[Do.styles,r`
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
        `];tableRef=(()=>new ds)();removeDetailsEl(t){for(const e of t.childNodes)if("TR"===e.tagName)for(const t of e.childNodes)for(const e of t.childNodes)"SL-DETAILS"===e.tagName&&t.removeChild(e);return t}copyTable(){const t=window.getSelection();t.removeAllRanges();const e=document.createRange();e.selectNodeContents(this.tableRef.value),t.addRange(e),this.removeDetailsEl(t.anchorNode),document.execCommand("copy"),t.removeAllRanges(),this.requestUpdate()}parseMetric(t){const e=t[0].split("|");return O`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,o]=t.split("|");return O`
            <td class="td-value">
                ${o?O`<abbr title=${o}>${e}</abbr>`:O`${e}`}
            </td>
        `}async parseSrc(){let t,e=O``;for await(const o of this.makeTextFileLineIterator(this.file)){const s=o.split(";"),i=s[0];if(s.shift(),"H"===i)for(const t of s)e=O`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===i)t=this.parseMetric(s);else{const o=O`${s.map((t=>this.parseSummaryFunc(t)))}`;e=O`
                    ${e}
                    <tr>
                      ${t}
                      ${o}
                    </tr>
                `,t&&(t=void 0)}}return e=O`<table ${hs(this.tableRef)} width=${this.getWidth(this.cols)}>${e}</table>`,O`
            <div style="display:flex;">
                ${e}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}}customElements.define("sc-smry-tbl",us);class ps extends Zo{static styles=r`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},fpreviews:{type:Array},smrytblpath:{type:String},smrytblfile:{type:Blob}};visibleTemplate(){return this.smrytblpath&&!this.smrytblfile&&fetch(this.smrytblpath).then((t=>t.blob())).then((t=>{this.smrytblfile=t})),O`
            <br>
            ${this.smrytblfile?O`<sc-smry-tbl .file="${this.smrytblfile}"></sc-smry-tbl>`:O``}
            ${this.fpreviews?this.fpreviews.map((t=>O`
                    <sc-file-preview .title=${t.title} .diff=${t.diff} .paths=${t.paths}></sc-file-preview>
                    <br>
                `)):O``}
            <div class="grid">
                ${this.paths?this.paths.map((t=>O`
                    <sc-diagram path="${t}"></sc-diagram>
                    `)):O``}
            </div>
        `}render(){return super.render()}}customElements.define("sc-data-tab",ps);class bs extends ot{static styles=r`
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
    `;static properties={tabs:{type:Object}};tabTemplate(t){return t.tabs?O`
                <sl-tab-group>
                    ${t.tabs.map((t=>O`
                        <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                        <sl-tab-panel class="tab-panel" id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                    `))}
                </sl-tab-group>
        `:O`
            <sc-data-tab tabname=${t.name} .smrytblpath=${t.smrytblpath} .smrytblfile=${t.smrytblfile} .paths=${t.ppaths} .fpreviews=${t.fpreviews} .dir=${t.dir}></sc-data-tab>
        `}render(){return this.tabs?O`
            <sl-tab-group>
                ${this.tabs.map((t=>O`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
      `:O``}}customElements.define("sc-tab-group",bs);class vs extends ot{static properties={introtbl:{type:Object},src:{type:String},reportInfo:{type:Object},toolname:{type:String},titleDescr:{type:String},tabs:{type:Object},fetchFailed:{type:Boolean,attribute:!1}};static styles=r`
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

        // Hide the close button as the dialog is not closable.
        sl-dialog::part(close-button) {
            visibility: hidden;
        }
    `;get _corsWarning(){return this.renderRoot.querySelector(".cors-warning")}initRepProps(){this.toolname=this.reportInfo.toolname,this.titleDescr=this.reportInfo.title_descr}parseReportInfo(t){this.reportInfo=t,this.initRepProps(),fetch(t.intro_tbl).then((t=>t.blob())).then((t=>{this.introtbl=t})),fetch(t.tab_file).then((t=>t.json())).then((async t=>{this.tabs=t}))}connectedCallback(){fetch(this.src).then((t=>t.json())).then((t=>this.parseReportInfo(t))).catch((t=>{if(!(t instanceof TypeError))throw t;this.fetchFailed=!0})),super.connectedCallback()}updated(t){t.has("fetchFailed")&&this.fetchFailed&&this._corsWarning.addEventListener("sl-request-close",(t=>{t.preventDefault()}))}corsWarning(){return O`
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
        `}findFile(t){const e=Object.keys(this.files);for(const o of e)if(o.endsWith(t))return this.files[o];throw Error(`unable to find an uploaded file ending with '${t}'.`)}async extractTabs(t,e){for(const o of t)o.smrytblpath&&(o.smrytblfile=e?await fetch(o.smrytblpath).then((t=>t.blob())):this.findFile(o.smrytblpath)),o.tabs&&(o.tabs=await this.extractTabs(o.tabs,e));return t}async processUploadedFiles(){const t=this.renderRoot.getElementById("upload-files");this.files={};for(const e of t.files)this.files[e.webkitRelativePath]=e;const e=await this.findFile("report_info.json").arrayBuffer();this.reportInfo=JSON.parse((new TextDecoder).decode(e)),this.introtbl=this.findFile(this.reportInfo.intro_tbl);const o=await this.findFile(this.reportInfo.tab_file).arrayBuffer().then((t=>JSON.parse((new TextDecoder).decode(t))));this.tabs=await this.extractTabs(o,!1),this.initRepProps(),this.fetchFailed=!1}constructor(){super(),this.fetchFailed=!1,this.reportInfo={}}render(){return this.fetchFailed?this.corsWarning():O`
            <div class="report-head">
                ${this.toolname?O`<h1 class="report-title">${this.toolname} report</h1>`:O``}
                ${this.titleDescr?O`
                        <p class="title_descr">${this.titleDescr}</p>
                        <br>
                    `:O``}
                ${this.introtbl?O`<sc-intro-tbl .file=${this.introtbl}></sc-intro-tbl>`:O``}
            </div>
            <br>
            ${this.tabs?O`<sc-tab-group .tabs=${this.tabs}></sc-tab-group>`:O``}
        `}}customElements.define("sc-report-page",vs),co("shoelace")})();