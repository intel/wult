/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),s=new Map;class i{constructor(t,s){if(this._$cssResult$=!0,s!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=s.get(this.cssText);return t&&void 0===e&&(s.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const r=t=>new i("string"==typeof t?t:t+"",e),o=(t,...s)=>{const r=1===t.length?t[0]:s.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new i(r,e)},n=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return r(e)})(t):t;var a;const l=window.trustedTypes,h=l?l.emptyScript:"",c=window.reactiveElementPolyfillSupport,d={toAttribute(t,e){switch(e){case Boolean:t=t?h:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},p=(t,e)=>e!==t&&(e==e||t==t),u={attribute:!0,type:String,converter:d,reflect:!1,hasChanged:p};class v extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=u){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const r=this[t];this[e]=i,this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||u}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const s=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{t?e.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const s=document.createElement("style"),i=window.litNonce;void 0!==i&&s.setAttribute("nonce",i),s.textContent=t.cssText,e.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=u){var i,r;const o=this.constructor._$Eh(t,s);if(void 0!==o&&!0===s.reflect){const n=(null!==(r=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==r?r:d.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$Ei=null}}_$AK(t,e){var s,i,r;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==r?r:d.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var b;v.finalized=!0,v.elementProperties=new Map,v.elementStyles=[],v.shadowRootOptions={mode:"open"},null==c||c({ReactiveElement:v}),(null!==(a=globalThis.reactiveElementVersions)&&void 0!==a?a:globalThis.reactiveElementVersions=[]).push("1.2.1");const g=globalThis.trustedTypes,m=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,f=`lit$${(Math.random()+"").slice(9)}$`,$="?"+f,y=`<${$}>`,_=document,w=(t="")=>_.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,E=Array.isArray,S=t=>{var e;return E(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},x=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,C=/-->/g,k=/>/g,T=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,U=/'/g,P=/"/g,M=/^(?:script|style|textarea)$/i,O=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),z=O(1),H=(O(2),Symbol.for("lit-noChange")),N=Symbol.for("lit-nothing"),L=new WeakMap,R=(t,e,s)=>{var i,r;const o=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=o._$litPart$;if(void 0===n){const t=null!==(r=null==s?void 0:s.renderBefore)&&void 0!==r?r:null;o._$litPart$=n=new F(e.insertBefore(w(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n},B=_.createTreeWalker(_,129,null,!1),j=(t,e)=>{const s=t.length-1,i=[];let r,o=2===e?"<svg>":"",n=x;for(let e=0;e<s;e++){const s=t[e];let a,l,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,l=n.exec(s),null!==l);)c=n.lastIndex,n===x?"!--"===l[1]?n=C:void 0!==l[1]?n=k:void 0!==l[2]?(M.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=T):void 0!==l[3]&&(n=T):n===T?">"===l[0]?(n=null!=r?r:x,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?T:'"'===l[3]?P:U):n===P||n===U?n=T:n===C||n===k?n=x:(n=T,r=void 0);const d=n===T&&t[e+1].startsWith("/>")?" ":"";o+=n===x?s+y:h>=0?(i.push(a),s.slice(0,h)+"$lit$"+s.slice(h)+f+d):s+f+(-2===h?(i.push(void 0),e):d)}const a=o+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==m?m.createHTML(a):a,i]};class I{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,o=0;const n=t.length-1,a=this.parts,[l,h]=j(t,e);if(this.el=I.createElement(l,s),B.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=B.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(f)){const s=h[o++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(f),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?q:"?"===e[1]?J:"@"===e[1]?Z:V})}else a.push({type:6,index:r})}for(const e of t)i.removeAttribute(e)}if(M.test(i.tagName)){const t=i.textContent.split(f),e=t.length-1;if(e>0){i.textContent=g?g.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],w()),B.nextNode(),a.push({type:2,index:++r});i.append(t[e],w())}}}else if(8===i.nodeType)if(i.data===$)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=i.data.indexOf(f,t+1));)a.push({type:7,index:r}),t+=f.length-1}r++}}static createElement(t,e){const s=_.createElement("template");return s.innerHTML=t,s}}function D(t,e,s=t,i){var r,o,n,a;if(e===H)return e;let l=void 0!==i?null===(r=s._$Cl)||void 0===r?void 0:r[i]:s._$Cu;const h=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==h&&(null===(o=null==l?void 0:l._$AO)||void 0===o||o.call(l,!1),void 0===h?l=void 0:(l=new h(t),l._$AT(t,s,i)),void 0!==i?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[i]=l:s._$Cu=l),void 0!==l&&(e=D(t,l._$AS(t,e.values),l,i)),e}class W{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,r=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:_).importNode(s,!0);B.currentNode=r;let o=B.nextNode(),n=0,a=0,l=i[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new F(o,o.nextSibling,this,t):1===l.type?e=new l.ctor(o,l.name,l.strings,this,t):6===l.type&&(e=new G(o,this,t)),this.v.push(e),l=i[++a]}n!==(null==l?void 0:l.index)&&(o=B.nextNode(),n++)}return r}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class F{constructor(t,e,s,i){var r;this.type=2,this._$AH=N,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(r=null==i?void 0:i.isConnected)||void 0===r||r}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=D(this,t,e),A(t)?t===N||null==t||""===t?(this._$AH!==N&&this._$AR(),this._$AH=N):t!==this._$AH&&t!==H&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):S(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==N&&A(this._$AH)?this._$AA.nextSibling.data=t:this.S(_.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,r="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=I.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===r)this._$AH.m(s);else{const t=new W(r,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=L.get(t.strings);return void 0===e&&L.set(t.strings,e=new I(t)),e}A(t){E(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const r of t)i===e.length?e.push(s=new F(this.M(w()),this.M(w()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class V{constructor(t,e,s,i,r){this.type=1,this._$AH=N,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=N}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const r=this.strings;let o=!1;if(void 0===r)t=D(this,t,e,0),o=!A(t)||t!==this._$AH&&t!==H,o&&(this._$AH=t);else{const i=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=D(this,i[s+n],e,n),a===H&&(a=this._$AH[n]),o||(o=!A(a)||a!==this._$AH[n]),a===N?t=N:t!==N&&(t+=(null!=a?a:"")+r[n+1]),this._$AH[n]=a}o&&!i&&this.k(t)}k(t){t===N?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class q extends V{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===N?void 0:t}}const K=g?g.emptyScript:"";class J extends V{constructor(){super(...arguments),this.type=4}k(t){t&&t!==N?this.element.setAttribute(this.name,K):this.element.removeAttribute(this.name)}}class Z extends V{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=D(this,t,e,0))&&void 0!==s?s:N)===H)return;const i=this._$AH,r=t===N&&i!==N||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==N&&(i===N||r);r&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}}class G{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){D(this,t)}}const X={P:"$lit$",V:f,L:$,I:1,N:j,R:W,D:S,j:D,H:F,O:V,F:J,B:Z,W:q,Z:G},Q=window.litHtmlPolyfillSupport;var Y,tt;null==Q||Q(I,F),(null!==(b=globalThis.litHtmlVersions)&&void 0!==b?b:globalThis.litHtmlVersions=[]).push("2.1.2");class et extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=R(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return H}}et.finalized=!0,et._$litElement$=!0,null===(Y=globalThis.litElementHydrateSupport)||void 0===Y||Y.call(globalThis,{LitElement:et});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:et}),(null!==(tt=globalThis.litElementVersions)&&void 0!==tt?tt:globalThis.litElementVersions=[]).push("3.1.2");class it extends et{static styles=o`
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
    `;getWidth(t){const e=Object.keys(t).length;return Math.min(100,20*e)}}customElements.define("report-table",it),customElements.define("intro-tbl",class extends it{static properties={introtbl:{type:Object}};connectedCallback(){super.connectedCallback(),this.link_keys=this.introtbl.link_keys,delete this.introtbl.link_keys}render(){return this.introtbl?z`
            <table width="${this.getWidth(this.introtbl)}%">
            <tr>
            ${Object.keys(this.introtbl).map((t=>z`<th>${t} </th>`))}
            </tr>
            ${Object.entries(this.introtbl.Title).map((([t,e])=>z`
                <tr>
                <td class="td-colname"> ${e} </td>
                ${Object.entries(this.introtbl).map((([s,i])=>"Title"!==s?z`<td class="td-value"> ${this.link_keys.includes(t)?i[t]?z`<a href=${i[t]}> ${e} </a>`:"Not available":i[t]} </td>`:z``))}
                </tr>
                `))}
            </table>
        `:z``}}),Object.create;var rt=Object.defineProperty,ot=Object.defineProperties,nt=Object.getOwnPropertyDescriptor,at=Object.getOwnPropertyDescriptors,lt=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),ht=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),ct=Object.prototype.propertyIsEnumerable,dt=(t,e,s)=>e in t?rt(t,e,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[e]=s,pt=(t,e)=>{for(var s in e||(e={}))ht.call(e,s)&&dt(t,s,e[s]);if(lt)for(var s of lt(e))ct.call(e,s)&&dt(t,s,e[s]);return t},ut=(t,e)=>ot(t,at(e)),vt=(t,e,s,i)=>{for(var r,o=i>1?void 0:i?nt(e,s):e,n=t.length-1;n>=0;n--)(r=t[n])&&(o=(i?r(e,s,o):r(o))||o);return i&&o&&rt(e,s,o),o};function bt(t,e,s){return new Promise((async i=>{if((null==s?void 0:s.duration)===1/0)throw new Error("Promise-based animations must be finite.");const r=t.animate(e,ut(pt({},s),{duration:gt()?0:s.duration}));r.addEventListener("cancel",i,{once:!0}),r.addEventListener("finish",i,{once:!0})}))}function gt(){const t=window.matchMedia("(prefers-reduced-motion: reduce)");return null==t?void 0:t.matches}function mt(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const s=requestAnimationFrame(e);t.addEventListener("cancel",(()=>s),{once:!0}),t.addEventListener("finish",(()=>s),{once:!0}),t.cancel()})))))}var ft=new Map,$t=new WeakMap;function yt(t,e){ft.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function _t(t,e){const s=$t.get(t);if(s&&s[e])return s[e];return ft.get(e)||{keyframes:[],options:{duration:0}}}var wt,At=t=>(...e)=>({_$litDirective$:t,values:e}),Et=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},St=globalThis.trustedTypes,xt=St?St.createPolicy("lit-html",{createHTML:t=>t}):void 0,Ct=`lit$${(Math.random()+"").slice(9)}$`,kt="?"+Ct,Tt=`<${kt}>`,Ut=document,Pt=(t="")=>Ut.createComment(t),Mt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Ot=Array.isArray,zt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ht=/-->/g,Nt=/>/g,Lt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,Rt=/'/g,Bt=/"/g,jt=/^(?:script|style|textarea)$/i,It=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),Dt=It(1),Wt=(It(2),Symbol.for("lit-noChange")),Ft=Symbol.for("lit-nothing"),Vt=new WeakMap,qt=Ut.createTreeWalker(Ut,129,null,!1),Kt=class{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,o=0;const n=t.length-1,a=this.parts,[l,h]=((t,e)=>{const s=t.length-1,i=[];let r,o=2===e?"<svg>":"",n=zt;for(let e=0;e<s;e++){const s=t[e];let a,l,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,l=n.exec(s),null!==l);)c=n.lastIndex,n===zt?"!--"===l[1]?n=Ht:void 0!==l[1]?n=Nt:void 0!==l[2]?(jt.test(l[2])&&(r=RegExp("</"+l[2],"g")),n=Lt):void 0!==l[3]&&(n=Lt):n===Lt?">"===l[0]?(n=null!=r?r:zt,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Lt:'"'===l[3]?Bt:Rt):n===Bt||n===Rt?n=Lt:n===Ht||n===Nt?n=zt:(n=Lt,r=void 0);const d=n===Lt&&t[e+1].startsWith("/>")?" ":"";o+=n===zt?s+Tt:h>=0?(i.push(a),s.slice(0,h)+"$lit$"+s.slice(h)+Ct+d):s+Ct+(-2===h?(i.push(void 0),e):d)}const a=o+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==xt?xt.createHTML(a):a,i]})(t,e);if(this.el=Kt.createElement(l,s),qt.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=qt.nextNode())&&a.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(Ct)){const s=h[o++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(Ct),e=/([.?@])?(.*)/.exec(s);a.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Xt:"?"===e[1]?Yt:"@"===e[1]?te:Gt})}else a.push({type:6,index:r})}for(const e of t)i.removeAttribute(e)}if(jt.test(i.tagName)){const t=i.textContent.split(Ct),e=t.length-1;if(e>0){i.textContent=St?St.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],Pt()),qt.nextNode(),a.push({type:2,index:++r});i.append(t[e],Pt())}}}else if(8===i.nodeType)if(i.data===kt)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=i.data.indexOf(Ct,t+1));)a.push({type:7,index:r}),t+=Ct.length-1}r++}}static createElement(t,e){const s=Ut.createElement("template");return s.innerHTML=t,s}};function Jt(t,e,s=t,i){var r,o,n,a;if(e===Wt)return e;let l=void 0!==i?null===(r=s._$Cl)||void 0===r?void 0:r[i]:s._$Cu;const h=Mt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==h&&(null===(o=null==l?void 0:l._$AO)||void 0===o||o.call(l,!1),void 0===h?l=void 0:(l=new h(t),l._$AT(t,s,i)),void 0!==i?(null!==(n=(a=s)._$Cl)&&void 0!==n?n:a._$Cl=[])[i]=l:s._$Cu=l),void 0!==l&&(e=Jt(t,l._$AS(t,e.values),l,i)),e}var Zt=class{constructor(t,e,s,i){var r;this.type=2,this._$AH=Ft,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(r=null==i?void 0:i.isConnected)||void 0===r||r}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Jt(this,t,e),Mt(t)?t===Ft||null==t||""===t?(this._$AH!==Ft&&this._$AR(),this._$AH=Ft):t!==this._$AH&&t!==Wt&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):(t=>{var e;return Ot(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==Ft&&Mt(this._$AH)?this._$AA.nextSibling.data=t:this.S(Ut.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,r="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Kt.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===r)this._$AH.m(s);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,r=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Ut).importNode(s,!0);qt.currentNode=r;let o=qt.nextNode(),n=0,a=0,l=i[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new Zt(o,o.nextSibling,this,t):1===l.type?e=new l.ctor(o,l.name,l.strings,this,t):6===l.type&&(e=new ee(o,this,t)),this.v.push(e),l=i[++a]}n!==(null==l?void 0:l.index)&&(o=qt.nextNode(),n++)}return r}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}(r,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=Vt.get(t.strings);return void 0===e&&Vt.set(t.strings,e=new Kt(t)),e}A(t){Ot(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const r of t)i===e.length?e.push(s=new Zt(this.M(Pt()),this.M(Pt()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Gt=class{constructor(t,e,s,i,r){this.type=1,this._$AH=Ft,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=Ft}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const r=this.strings;let o=!1;if(void 0===r)t=Jt(this,t,e,0),o=!Mt(t)||t!==this._$AH&&t!==Wt,o&&(this._$AH=t);else{const i=t;let n,a;for(t=r[0],n=0;n<r.length-1;n++)a=Jt(this,i[s+n],e,n),a===Wt&&(a=this._$AH[n]),o||(o=!Mt(a)||a!==this._$AH[n]),a===Ft?t=Ft:t!==Ft&&(t+=(null!=a?a:"")+r[n+1]),this._$AH[n]=a}o&&!i&&this.k(t)}k(t){t===Ft?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Xt=class extends Gt{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===Ft?void 0:t}},Qt=St?St.emptyScript:"",Yt=class extends Gt{constructor(){super(...arguments),this.type=4}k(t){t&&t!==Ft?this.element.setAttribute(this.name,Qt):this.element.removeAttribute(this.name)}},te=class extends Gt{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=Jt(this,t,e,0))&&void 0!==s?s:Ft)===Wt)return;const i=this._$AH,r=t===Ft&&i!==Ft||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==Ft&&(i===Ft||r);r&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}},ee=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){Jt(this,t)}},se=window.litHtmlPolyfillSupport;null==se||se(Kt,Zt),(null!==(wt=globalThis.litHtmlVersions)&&void 0!==wt?wt:globalThis.litHtmlVersions=[]).push("2.1.0");var ie,re,oe,ne=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ae=Symbol(),le=new Map,he=class{constructor(t,e){if(this._$cssResult$=!0,e!==ae)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=le.get(this.cssText);return ne&&void 0===t&&(le.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},ce=t=>new he("string"==typeof t?t:t+"",ae),de=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new he(s,ae)},pe=ne?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return ce(e)})(t):t,ue=window.trustedTypes,ve=ue?ue.emptyScript:"",be=window.reactiveElementPolyfillSupport,ge={toAttribute(t,e){switch(e){case Boolean:t=t?ve:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},me=(t,e)=>e!==t&&(e==e||t==t),fe={attribute:!0,type:String,converter:ge,reflect:!1,hasChanged:me},$e=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=fe){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const r=this[t];this[e]=i,this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||fe}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(pe(t))}else void 0!==t&&e.push(pe(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,ne?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=fe){var i,r;const o=this.constructor._$Eh(t,s);if(void 0!==o&&!0===s.reflect){const n=(null!==(r=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==r?r:ge.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$Ei=null}}_$AK(t,e){var s,i,r;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==r?r:ge.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||me)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}};$e.finalized=!0,$e.elementProperties=new Map,$e.elementStyles=[],$e.shadowRootOptions={mode:"open"},null==be||be({ReactiveElement:$e}),(null!==(ie=globalThis.reactiveElementVersions)&&void 0!==ie?ie:globalThis.reactiveElementVersions=[]).push("1.1.0");var ye=class extends $e{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,s)=>{var i,r;const o=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=o._$litPart$;if(void 0===n){const t=null!==(r=null==s?void 0:s.renderBefore)&&void 0!==r?r:null;o._$litPart$=n=new Zt(e.insertBefore(Pt(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return Wt}};ye.finalized=!0,ye._$litElement$=!0,null===(re=globalThis.litElementHydrateSupport)||void 0===re||re.call(globalThis,{LitElement:ye});var _e=globalThis.litElementPolyfillSupport;null==_e||_e({LitElement:ye}),(null!==(oe=globalThis.litElementVersions)&&void 0!==oe?oe:globalThis.litElementVersions=[]).push("3.1.0");var we,Ae=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Ee=Symbol(),Se=new Map,xe=t=>new class{constructor(t,e){if(this._$cssResult$=!0,e!==Ee)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=Se.get(this.cssText);return Ae&&void 0===t&&(Se.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}}("string"==typeof t?t:t+"",Ee),Ce=Ae?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return xe(e)})(t):t,ke=window.trustedTypes,Te=ke?ke.emptyScript:"",Ue=window.reactiveElementPolyfillSupport,Pe={toAttribute(t,e){switch(e){case Boolean:t=t?Te:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},Me=(t,e)=>e!==t&&(e==e||t==t),Oe={attribute:!0,type:String,converter:Pe,reflect:!1,hasChanged:Me},ze=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=Oe){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const r=this[t];this[e]=i,this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Oe}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(Ce(t))}else void 0!==t&&e.push(Ce(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,Ae?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=Oe){var i,r;const o=this.constructor._$Eh(t,s);if(void 0!==o&&!0===s.reflect){const n=(null!==(r=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==r?r:Pe.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$Ei=null}}_$AK(t,e){var s,i,r;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),a=t.converter,l=null!==(r=null!==(i=null===(s=a)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof a?a:null)&&void 0!==r?r:Pe.fromAttribute;this._$Ei=n,this[n]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||Me)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}};ze.finalized=!0,ze.elementProperties=new Map,ze.elementStyles=[],ze.shadowRootOptions={mode:"open"},null==Ue||Ue({ReactiveElement:ze}),(null!==(we=globalThis.reactiveElementVersions)&&void 0!==we?we:globalThis.reactiveElementVersions=[]).push("1.1.0");var He=At(class extends Et{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var s,i;if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.et=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(s=this.et)||void 0===s?void 0:s.has(t))&&this.st.add(t);return this.render(e)}const r=t.element.classList;this.st.forEach((t=>{t in e||(r.remove(t),this.st.delete(t))}));for(const t in e){const s=!!e[t];s===this.st.has(t)||(null===(i=this.et)||void 0===i?void 0:i.has(t))||(s?(r.add(t),this.st.add(t)):(r.remove(t),this.st.delete(t)))}return Wt}}),Ne=de`
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
`,Le=de`
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
`,Re=document.createElement("style");Re.textContent=Ne.toString(),document.head.append(Re);var Be=de`
  ${Le}

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
`;function je(t,e){return(s,i)=>{const{update:r}=s;e=Object.assign({waitUntilFirstUpdate:!1},e),s.update=function(s){if(s.has(t)){const r=s.get(t),o=this[t];r!==o&&((null==e?void 0:e.waitUntilFirstUpdate)&&!this.hasUpdated||this[i].call(this,r,o))}r.call(this,s)}}}function Ie(t,e,s){const i=new CustomEvent(e,Object.assign({bubbles:!0,cancelable:!1,composed:!0,detail:{}},s));return t.dispatchEvent(i),i}function De(t,e){return new Promise((s=>{t.addEventListener(e,(function i(r){r.target===t&&(t.removeEventListener(e,i),s())}))}))}var We=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:s,elements:i}=e;return{kind:s,elements:i,finisher(e){window.customElements.define(t,e)}}})(t,e),Fe=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?ut(pt({},e),{finisher(s){s.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(s){s.createProperty(e.key,t)}};function Ve(t){return(e,s)=>void 0!==s?((t,e,s)=>{e.constructor.createProperty(s,t)})(t,e,s):Fe(t,e)}function qe(t){return Ve(ut(pt({},t),{state:!0}))}function Ke(t,e){return(({finisher:t,descriptor:e})=>(s,i)=>{var r;if(void 0===i){const i=null!==(r=s.originalKey)&&void 0!==r?r:s.key,o=null!=e?{kind:"method",placement:"prototype",key:i,descriptor:e(s.key)}:ut(pt({},s),{key:i});return null!=t&&(o.finisher=function(e){t(e,i)}),o}{const r=s.constructor;void 0!==e&&Object.defineProperty(s,i,e(i)),null==t||t(r,i)}})({descriptor:s=>{const i={get(){var e,s;return null!==(s=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==s?s:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof s?Symbol():"__"+s;i.get=function(){var s,i;return void 0===this[e]&&(this[e]=null!==(i=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(t))&&void 0!==i?i:null),this[e]}}return i}})}var Je=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Ze=class extends ye{constructor(){super(...arguments),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}async show(){if(!this.open)return this.open=!0,De(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,De(this,"sl-after-hide")}async toast(){return new Promise((t=>{Je.parentElement||document.body.append(Je),Je.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{Je.removeChild(this),t(),Je.querySelector("sl-alert")||Je.remove()}),{once:!0})}))}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){Ie(this,"sl-show"),this.duration<1/0&&this.restartAutoHide(),await mt(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=_t(this,"alert.show");await bt(this.base,t,e),Ie(this,"sl-after-show")}else{Ie(this,"sl-hide"),clearTimeout(this.autoHideTimeout),await mt(this.base);const{keyframes:t,options:e}=_t(this,"alert.hide");await bt(this.base,t,e),this.base.hidden=!0,Ie(this,"sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}render(){return Dt`
      <div
        part="base"
        class=${He({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
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

        ${this.closable?Dt`
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
    `}};Ze.styles=Be,vt([Ke('[part="base"]')],Ze.prototype,"base",2),vt([Ve({type:Boolean,reflect:!0})],Ze.prototype,"open",2),vt([Ve({type:Boolean,reflect:!0})],Ze.prototype,"closable",2),vt([Ve({reflect:!0})],Ze.prototype,"variant",2),vt([Ve({type:Number})],Ze.prototype,"duration",2),vt([je("open",{waitUntilFirstUpdate:!0})],Ze.prototype,"handleOpenChange",1),vt([je("duration")],Ze.prototype,"handleDurationChange",1),Ze=vt([We("sl-alert")],Ze),yt("alert.show",{keyframes:[{opacity:0,transform:"scale(0.8)"},{opacity:1,transform:"scale(1)"}],options:{duration:250,easing:"ease"}}),yt("alert.hide",{keyframes:[{opacity:1,transform:"scale(1)"},{opacity:0,transform:"scale(0.8)"}],options:{duration:250,easing:"ease"}});var Ge=(()=>{const t=document.createElement("style");let e;try{document.head.appendChild(t),t.sheet.insertRule(":focus-visible { color: inherit }"),e=!0}catch(t){e=!1}finally{t.remove()}return e})(),Xe=ce(Ge?":focus-visible":":focus"),Qe=de`
  ${Le}

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

  .icon-button${Xe} {
    box-shadow: var(--sl-focus-ring);
  }
`,Ye=t=>null!=t?t:Ft,ts=class extends ye{constructor(){super(...arguments),this.label="",this.disabled=!1}render(){const t=!!this.href,e=Dt`
      <sl-icon
        name=${Ye(this.name)}
        library=${Ye(this.library)}
        src=${Ye(this.src)}
        aria-hidden="true"
      ></sl-icon>
    `;return t?Dt`
          <a
            part="base"
            class="icon-button"
            href=${Ye(this.href)}
            target=${Ye(this.target)}
            download=${Ye(this.download)}
            rel=${Ye(this.target?"noreferrer noopener":void 0)}
            role="button"
            aria-disabled=${this.disabled?"true":"false"}
            aria-label="${this.label}"
            tabindex=${this.disabled?"-1":"0"}
          >
            ${e}
          </a>
        `:Dt`
          <button
            part="base"
            class=${He({"icon-button":!0,"icon-button--disabled":this.disabled})}
            ?disabled=${this.disabled}
            type="button"
            aria-label=${this.label}
          >
            ${e}
          </button>
        `}};ts.styles=Qe,vt([Ke("button")],ts.prototype,"button",2),vt([Ve()],ts.prototype,"name",2),vt([Ve()],ts.prototype,"library",2),vt([Ve()],ts.prototype,"src",2),vt([Ve()],ts.prototype,"href",2),vt([Ve()],ts.prototype,"target",2),vt([Ve()],ts.prototype,"download",2),vt([Ve()],ts.prototype,"label",2),vt([Ve({type:Boolean,reflect:!0})],ts.prototype,"disabled",2),ts=vt([We("sl-icon-button")],ts);var es="";function ss(t){es=t}var is=[...document.getElementsByTagName("script")],rs=is.find((t=>t.hasAttribute("data-shoelace")));if(rs)ss(rs.getAttribute("data-shoelace"));else{const t=is.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let e="";t&&(e=t.getAttribute("src")),ss(e.split("/").slice(0,-1).join("/"))}var os={check:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">\n      <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},ns=[{name:"default",resolver:t=>`${es.replace(/\/$/,"")}/assets/icons/${t}.svg`},{name:"system",resolver:t=>os[t]?`data:image/svg+xml,${encodeURIComponent(os[t])}`:""}],as=[];function ls(t){return ns.filter((e=>e.name===t))[0]}var hs=new Map,cs=de`
  ${Le}

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
`,ds=class extends Et{constructor(t){if(super(t),this.it=Ft,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===Ft||null==t)return this.vt=void 0,this.it=t;if(t===Wt)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.vt;this.it=t;const e=[t];return e.raw=e,this.vt={_$litType$:this.constructor.resultType,strings:e,values:[]}}};ds.directiveName="unsafeHTML",ds.resultType=1,At(ds);var ps=class extends ds{};ps.directiveName="unsafeSVG",ps.resultType=2;var us=At(ps),vs=new DOMParser,bs=class extends ye{constructor(){super(...arguments),this.svg="",this.library="default"}connectedCallback(){super.connectedCallback(),as.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,as=as.filter((e=>e!==t))}getUrl(){const t=ls(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){const t=ls(this.library),e=this.getUrl();if(e)try{const s=await(t=>{if(hs.has(t))return hs.get(t);{const e=fetch(t).then((async t=>{if(t.ok){const e=document.createElement("div");e.innerHTML=await t.text();const s=e.firstElementChild;return{ok:t.ok,status:t.status,svg:s&&"svg"===s.tagName.toLowerCase()?s.outerHTML:""}}return{ok:t.ok,status:t.status,svg:null}}));return hs.set(t,e),e}})(e);if(e!==this.getUrl())return;if(s.ok){const e=vs.parseFromString(s.svg,"text/html").body.querySelector("svg");e?(t&&t.mutator&&t.mutator(e),this.svg=e.outerHTML,Ie(this,"sl-load")):(this.svg="",Ie(this,"sl-error",{detail:{status:s.status}}))}else this.svg="",Ie(this,"sl-error",{detail:{status:s.status}})}catch(t){Ie(this,"sl-error",{detail:{status:-1}})}else this.svg&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return Dt` <div
      part="base"
      class="icon"
      role=${Ye(t?"img":void 0)}
      aria-label=${Ye(t?this.label:void 0)}
      aria-hidden=${Ye(t?void 0:"true")}
    >
      ${us(this.svg)}
    </div>`}};bs.styles=cs,vt([qe()],bs.prototype,"svg",2),vt([Ve()],bs.prototype,"name",2),vt([Ve()],bs.prototype,"src",2),vt([Ve()],bs.prototype,"label",2),vt([Ve()],bs.prototype,"library",2),vt([je("name"),je("src"),je("library")],bs.prototype,"setIcon",1),bs=vt([We("sl-icon")],bs);var gs,ms=de`
  ${Le}

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
`,fs=new Set,$s=new MutationObserver(ws),ys=new Map,_s=document.documentElement.lang||navigator.language;function ws(){_s=document.documentElement.lang||navigator.language,[...fs.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}$s.observe(document.documentElement,{attributes:!0,attributeFilter:["lang"]});var As=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){fs.add(this.host)}hostDisconnected(){fs.delete(this.host)}term(t,...e){return function(t,e,...s){const i=t.toLowerCase().slice(0,2),r=t.length>2?t.toLowerCase():"",o=ys.get(r),n=ys.get(i);let a;if(o&&o[e])a=o[e];else if(n&&n[e])a=n[e];else{if(!gs||!gs[e])return console.error(`No translation found for: ${e}`),e;a=gs[e]}return"function"==typeof a?a(...s):a}(this.host.lang||_s,t,...e)}date(t,e){return function(t,e,s){return e=new Date(e),new Intl.DateTimeFormat(t,s).format(e)}(this.host.lang||_s,t,e)}number(t,e){return function(t,e,s){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(t,s).format(e)}(this.host.lang||_s,t,e)}relativeTime(t,e,s){return function(t,e,s,i){return new Intl.RelativeTimeFormat(t,i).format(e,s)}(this.host.lang||_s,t,e,s)}};function Es(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}function Ss(t,e,s="vertical",i="smooth"){const r=Es(t,e),o=r.top+e.scrollTop,n=r.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,h=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==s&&"both"!==s||(n<a?e.scrollTo({left:n,behavior:i}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:i})),"vertical"!==s&&"both"!==s||(o<h?e.scrollTo({top:o,behavior:i}):o+t.clientHeight>c&&e.scrollTo({top:o-e.offsetHeight+t.clientHeight,behavior:i}))}!function(...t){t.map((t=>{const e=t.$code.toLowerCase();ys.set(e,t),gs||(gs=t)})),ws()}({$code:"en",$name:"English",$dir:"ltr",close:"Close",copy:"Copy",progress:"Progress",resize:"Resize",scroll_to_end:"Scroll to end",scroll_to_start:"Scroll to start",select_a_color_from_the_screen:"Select a color from the screen",toggle_color_format:"Toggle color format"});var xs=class extends ye{constructor(){super(...arguments),this.localize=new As(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(this.getActiveTab()||this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t=!1){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement;if(e&&"sl-tab"===e.tagName.toLowerCase()){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&"ArrowLeft"===t.key||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s=Math.max(0,s-1):(["top","bottom"].includes(this.placement)&&"ArrowRight"===t.key||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&(s=Math.min(this.tabs.length-1,s+1)),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Ss(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.nav&&(this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth)}setActiveTab(t,e){if(e=Object.assign({emitEvents:!0,scrollBehavior:"auto"},e),t&&t!==this.activeTab&&!t.disabled){const s=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>t.active=t.name===this.activeTab.panel)),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Ss(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(s&&Ie(this,"sl-tab-hide",{detail:{name:s.panel}}),Ie(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.map((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){if(this.indicator){if(!this.getActiveTab())return void(this.indicator.style.display="none");this.indicator.style.display="block",this.repositionIndicator()}}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,s=t.clientHeight,i=Es(t,this.nav),r=i.top+this.nav.scrollTop,o=i.left+this.nav.scrollLeft;switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=`translateX(${o}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${s}px`,this.indicator.style.transform=`translateY(${r}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.panels=this.getAllPanels(),this.syncIndicator()}render(){return Dt`
      <div
        part="base"
        class=${He({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?Dt`
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

          ${this.hasScrollControls?Dt`
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
    `}};xs.styles=ms,vt([Ke(".tab-group")],xs.prototype,"tabGroup",2),vt([Ke(".tab-group__body")],xs.prototype,"body",2),vt([Ke(".tab-group__nav")],xs.prototype,"nav",2),vt([Ke(".tab-group__indicator")],xs.prototype,"indicator",2),vt([qe()],xs.prototype,"hasScrollControls",2),vt([Ve()],xs.prototype,"placement",2),vt([Ve()],xs.prototype,"activation",2),vt([Ve({attribute:"no-scroll-controls",type:Boolean})],xs.prototype,"noScrollControls",2),vt([Ve()],xs.prototype,"lang",2),vt([je("noScrollControls")],xs.prototype,"updateScrollControls",1),vt([je("placement")],xs.prototype,"syncIndicator",1),xs=vt([We("sl-tab-group")],xs);var Cs=de`
  ${Le}

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

  .tab${Xe}:not(.tab--disabled) {
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
`,ks=0,Ts=class extends ye{constructor(){super(...arguments),this.localize=new As(this),this.componentId="sl-tab-"+ ++ks,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Ie(this,"sl-close")}render(){return this.id=this.id||this.componentId,Dt`
      <div
        part="base"
        class=${He({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        role="tab"
        aria-disabled=${this.disabled?"true":"false"}
        aria-selected=${this.active?"true":"false"}
        tabindex=${this.disabled||!this.active?"-1":"0"}
      >
        <slot></slot>
        ${this.closable?Dt`
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
    `}};Ts.styles=Cs,vt([Ke(".tab")],Ts.prototype,"tab",2),vt([Ve({reflect:!0})],Ts.prototype,"panel",2),vt([Ve({type:Boolean,reflect:!0})],Ts.prototype,"active",2),vt([Ve({type:Boolean})],Ts.prototype,"closable",2),vt([Ve({type:Boolean,reflect:!0})],Ts.prototype,"disabled",2),vt([Ve()],Ts.prototype,"lang",2),Ts=vt([We("sl-tab")],Ts);var Us=de`
  ${Le}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }
`,Ps=0,Ms=class extends ye{constructor(){super(...arguments),this.componentId="sl-tab-panel-"+ ++Ps,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id||this.componentId}render(){return this.style.display=this.active?"block":"none",Dt`
      <div part="base" class="tab-panel" role="tabpanel" aria-hidden=${this.active?"false":"true"}>
        <slot></slot>
      </div>
    `}};Ms.styles=Us,vt([Ve({reflect:!0})],Ms.prototype,"name",2),vt([Ve({type:Boolean,reflect:!0})],Ms.prototype,"active",2),Ms=vt([We("sl-tab-panel")],Ms);const{H:Os}=X,zs=(t,e)=>{var s,i;return void 0===e?void 0!==(null===(s=t)||void 0===s?void 0:s._$litType$):(null===(i=t)||void 0===i?void 0:i._$litType$)===e},Hs=()=>document.createComment(""),Ns=(t,e,s)=>{var i;const r=t._$AA.parentNode,o=void 0===e?t._$AB:e._$AA;if(void 0===s){const e=r.insertBefore(Hs(),o),i=r.insertBefore(Hs(),o);s=new Os(e,i,t,t.options)}else{const e=s._$AB.nextSibling,n=s._$AM,a=n!==t;if(a){let e;null===(i=s._$AQ)||void 0===i||i.call(s,t),s._$AM=t,void 0!==s._$AP&&(e=t._$AU)!==n._$AU&&s._$AP(e)}if(e!==o||a){let t=s._$AA;for(;t!==e;){const e=t.nextSibling;r.insertBefore(t,o),t=e}}}return s},Ls={},Rs=(t,e=Ls)=>t._$AH=e,Bs=t=>t._$AH,js=(Is=class extends class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}{constructor(t){super(t),this.tt=new WeakMap}render(t){return[t]}update(t,[e]){if(zs(this.it)&&(!zs(e)||this.it.strings!==e.strings)){const e=Bs(t).pop();let s=this.tt.get(this.it.strings);if(void 0===s){const t=document.createDocumentFragment();s=R(N,t),s.setConnected(!1),this.tt.set(this.it.strings,s)}Rs(s,[e]),Ns(s,void 0,e)}if(zs(e)){if(!zs(this.it)||this.it.strings!==e.strings){const s=this.tt.get(e.strings);if(void 0!==s){const e=Bs(s).pop();(t=>{t._$AR()})(t),Ns(t,void 0,e),Rs(t,[e])}}this.it=e}else this.it=void 0;return this.render(e)}},(...t)=>({_$litDirective$:Is,values:t}));var Is;class Ds extends et{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(t,e){for(const e of t)"active"===e.attributeName&&(this.tabname===e.target.id?this.visible=!0:this.visible=!1)}connectedCallback(){super.connectedCallback();const t=this.checkVisible.bind(this);this.observer=new MutationObserver(t),this.observer.observe(this.parentElement,{attributes:!0})}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return z`
      ${js(this.visible?z`${this.visibleTemplate()}`:z``)}`}}customElements.define("wult-tab",Ds);class Ws extends et{static styles=o`
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
  `;static properties={path:{type:String}};render(){return z`
            <div class="plot">
                <iframe seamless="seamless" frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
            </div>
        `}}customElements.define("diagram-element",Ws),customElements.define("smry-tbl",class extends it{static properties={src:{type:String},template:{attribute:!1}};parseMetric(t){const e=t[0].split("|");return z`
        <td rowspan=${t[1]} class="td-colname">
            <abbr title=${e[1]}>${e[0]}</abbr>
        </td>
      `}parseSummaryFunc(t){const[e,s]=t.split("|");return z`
        <td class="td-value">
            ${s?z`<abbr title=${s}>${e}</abbr>`:z`${e}`}
        </td>
      `}async parseSrc(){let t,e=z``;for await(const s of async function*(t){const e=new TextDecoder("utf-8"),s=(await fetch(t)).body.getReader();let{value:i,done:r}=await s.read();i=i?e.decode(i,{stream:!0}):"";const o=/\r\n|\n|\r/gm;let n=0;for(;;){const t=o.exec(i);if(t)yield i.substring(n,t.index),n=o.lastIndex;else{if(r)break;const t=i.substr(n);({value:i,done:r}=await s.read()),i=t+(i?e.decode(i,{stream:!0}):""),n=o.lastIndex=0}}n<i.length&&(yield i.substr(n))}(this.src)){const i=s.split(";"),r=i[0];if(i.shift(),"H"===r)for(const t of i)e=z`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===r)t=this.parseMetric(i);else{const s=z`
            ${i.map((t=>this.parseSummaryFunc(t)))}
          `;e=z`
          ${e}
          <tr>
            ${t}
            ${s}
          </tr>
          `,t&&(t=void 0)}}return e}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}getWidth(){return Math.min(100,20*(this.cols-2))}render(){return this.template?z`
            <table width="${this.getWidth(this.smrystbl)}%">
            ${this.template}
            </table>
        `:z``}});class Fs extends Ds{static styles=o`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;static properties={paths:{type:Array},smrytblpath:{type:String}};visibleTemplate(){return z`
            <br>
            <smry-tbl .src="${this.tabname}/${this.smrytblpath}"></smry-tbl>
            <div class="grid">
            ${this.paths.map((t=>z`<diagram-element path="${this.tabname}/${t}" ></diagram-element>`))}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",Fs);class Vs extends et{static styles=o`
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
    `;static properties={tabFile:{type:String},tabs:{type:Object,attribute:!1},fetchFailed:{type:Boolean,attribute:!1}};connectedCallback(){super.connectedCallback(),fetch(this.tabFile).then((t=>t.json())).then((t=>{this.tabs=t})).catch((t=>{if(!(t instanceof TypeError))throw t;this.fetchFailed=!0}))}corsWarning(){return z`
        <sl-alert variant="danger" open>
          Warning: it looks like you might be trying to view this report locally. See our
          documentation on how to do that 
          <a href="https://intel.github.io/wult/pages/howto.html#open-wult-reports-locally">
            here.</a>
        </sl-alert>
      `}tabTemplate(t){return t.tabs?z`
          <sl-tab-group>
            ${t.tabs.map((t=>z`
             <sl-tab slot="nav" panel="${t.name}">${t.name}</sl-tab>
             <sl-tab-panel id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
             `))}
          </sl-tab-group>
        `:z`
      <wult-metric-tab tabname="${t.name}" .smrytblpath="${t.smrytblpath}" .paths="${t.ppaths}" .dir="${t.dir}" ></wult-metric-tab>
      `}render(){return this.fetchFailed?this.corsWarning():this.tabs?z`
            <sl-tab-group>
              ${this.tabs.map((t=>z`
                  <sl-tab slot="nav" panel="${t.name}">${t.name}</sl-tab>
                  <sl-tab-panel name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
          `:z``}}customElements.define("tab-group",Vs),ss("shoelace")})();