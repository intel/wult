/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),s=new Map;class i{constructor(t,s){if(this._$cssResult$=!0,s!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=s.get(this.cssText);return t&&void 0===e&&(s.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const n=t=>new i("string"==typeof t?t:t+"",e),r=(t,...s)=>{const n=1===t.length?t[0]:s.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new i(n,e)},l=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return n(e)})(t):t;var o;const a=window.trustedTypes,h=a?a.emptyScript:"",d=window.reactiveElementPolyfillSupport,c={toAttribute(t,e){switch(e){case Boolean:t=t?h:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},u=(t,e)=>e!==t&&(e==e||t==t),p={attribute:!0,type:String,converter:c,reflect:!1,hasChanged:u};class $ extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=p){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const n=this[t];this[e]=i,this.requestUpdate(t,n,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||p}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(l(t))}else void 0!==t&&e.push(l(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const s=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{t?e.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const s=document.createElement("style"),i=window.litNonce;void 0!==i&&s.setAttribute("nonce",i),s.textContent=t.cssText,e.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=p){var i,n;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const l=(null!==(n=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==n?n:c.toAttribute)(e,s.type);this._$Ei=t,null==l?this.removeAttribute(r):this.setAttribute(r,l),this._$Ei=null}}_$AK(t,e){var s,i,n;const r=this.constructor,l=r._$Eu.get(t);if(void 0!==l&&this._$Ei!==l){const t=r.getPropertyOptions(l),o=t.converter,a=null!==(n=null!==(i=null===(s=o)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof o?o:null)&&void 0!==n?n:c.fromAttribute;this._$Ei=l,this[l]=a(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||u)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var v;$.finalized=!0,$.elementProperties=new Map,$.elementStyles=[],$.shadowRootOptions={mode:"open"},null==d||d({ReactiveElement:$}),(null!==(o=globalThis.reactiveElementVersions)&&void 0!==o?o:globalThis.reactiveElementVersions=[]).push("1.0.2");const m=globalThis.trustedTypes,b=m?m.createPolicy("lit-html",{createHTML:t=>t}):void 0,_=`lit$${(Math.random()+"").slice(9)}$`,f="?"+_,g=`<${f}>`,y=document,A=(t="")=>y.createComment(t),w=t=>null===t||"object"!=typeof t&&"function"!=typeof t,E=Array.isArray,S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,C=/-->/g,x=/>/g,k=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,T=/'/g,U=/"/g,O=/^(?:script|style|textarea)$/i,P=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),H=P(1),N=(P(2),Symbol.for("lit-noChange")),M=Symbol.for("lit-nothing"),R=new WeakMap,j=y.createTreeWalker(y,129,null,!1),L=(t,e)=>{const s=t.length-1,i=[];let n,r=2===e?"<svg>":"",l=S;for(let e=0;e<s;e++){const s=t[e];let o,a,h=-1,d=0;for(;d<s.length&&(l.lastIndex=d,a=l.exec(s),null!==a);)d=l.lastIndex,l===S?"!--"===a[1]?l=C:void 0!==a[1]?l=x:void 0!==a[2]?(O.test(a[2])&&(n=RegExp("</"+a[2],"g")),l=k):void 0!==a[3]&&(l=k):l===k?">"===a[0]?(l=null!=n?n:S,h=-1):void 0===a[1]?h=-2:(h=l.lastIndex-a[2].length,o=a[1],l=void 0===a[3]?k:'"'===a[3]?U:T):l===U||l===T?l=k:l===C||l===x?l=S:(l=k,n=void 0);const c=l===k&&t[e+1].startsWith("/>")?" ":"";r+=l===S?s+g:h>=0?(i.push(o),s.slice(0,h)+"$lit$"+s.slice(h)+_+c):s+_+(-2===h?(i.push(void 0),e):c)}const o=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==b?b.createHTML(o):o,i]};class z{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let n=0,r=0;const l=t.length-1,o=this.parts,[a,h]=L(t,e);if(this.el=z.createElement(a,s),j.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=j.nextNode())&&o.length<l;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(_)){const s=h[r++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(_),e=/([.?@])?(.*)/.exec(s);o.push({type:1,index:n,name:e[2],strings:t,ctor:"."===e[1]?W:"?"===e[1]?J:"@"===e[1]?K:V})}else o.push({type:6,index:n})}for(const e of t)i.removeAttribute(e)}if(O.test(i.tagName)){const t=i.textContent.split(_),e=t.length-1;if(e>0){i.textContent=m?m.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],A()),j.nextNode(),o.push({type:2,index:++n});i.append(t[e],A())}}}else if(8===i.nodeType)if(i.data===f)o.push({type:2,index:n});else{let t=-1;for(;-1!==(t=i.data.indexOf(_,t+1));)o.push({type:7,index:n}),t+=_.length-1}n++}}static createElement(t,e){const s=y.createElement("template");return s.innerHTML=t,s}}function B(t,e,s=t,i){var n,r,l,o;if(e===N)return e;let a=void 0!==i?null===(n=s._$Cl)||void 0===n?void 0:n[i]:s._$Cu;const h=w(e)?void 0:e._$litDirective$;return(null==a?void 0:a.constructor)!==h&&(null===(r=null==a?void 0:a._$AO)||void 0===r||r.call(a,!1),void 0===h?a=void 0:(a=new h(t),a._$AT(t,s,i)),void 0!==i?(null!==(l=(o=s)._$Cl)&&void 0!==l?l:o._$Cl=[])[i]=a:s._$Cu=a),void 0!==a&&(e=B(t,a._$AS(t,e.values),a,i)),e}class I{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:y).importNode(s,!0);j.currentNode=n;let r=j.nextNode(),l=0,o=0,a=i[0];for(;void 0!==a;){if(l===a.index){let e;2===a.type?e=new D(r,r.nextSibling,this,t):1===a.type?e=new a.ctor(r,a.name,a.strings,this,t):6===a.type&&(e=new Z(r,this,t)),this.v.push(e),a=i[++o]}l!==(null==a?void 0:a.index)&&(r=j.nextNode(),l++)}return n}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class D{constructor(t,e,s,i){var n;this.type=2,this._$AH=M,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(n=null==i?void 0:i.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=B(this,t,e),w(t)?t===M||null==t||""===t?(this._$AH!==M&&this._$AR(),this._$AH=M):t!==this._$AH&&t!==N&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):(t=>{var e;return E(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==M&&w(this._$AH)?this._$AA.nextSibling.data=t:this.S(y.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,n="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=z.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.m(s);else{const t=new I(n,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=R.get(t.strings);return void 0===e&&R.set(t.strings,e=new z(t)),e}A(t){E(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const n of t)i===e.length?e.push(s=new D(this.M(A()),this.M(A()),this,this.options)):s=e[i],s._$AI(n),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class V{constructor(t,e,s,i,n){this.type=1,this._$AH=M,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=n,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=M}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const n=this.strings;let r=!1;if(void 0===n)t=B(this,t,e,0),r=!w(t)||t!==this._$AH&&t!==N,r&&(this._$AH=t);else{const i=t;let l,o;for(t=n[0],l=0;l<n.length-1;l++)o=B(this,i[s+l],e,l),o===N&&(o=this._$AH[l]),r||(r=!w(o)||o!==this._$AH[l]),o===M?t=M:t!==M&&(t+=(null!=o?o:"")+n[l+1]),this._$AH[l]=o}r&&!i&&this.k(t)}k(t){t===M?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class W extends V{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===M?void 0:t}}const q=m?m.emptyScript:"";class J extends V{constructor(){super(...arguments),this.type=4}k(t){t&&t!==M?this.element.setAttribute(this.name,q):this.element.removeAttribute(this.name)}}class K extends V{constructor(t,e,s,i,n){super(t,e,s,i,n),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=B(this,t,e,0))&&void 0!==s?s:M)===N)return;const i=this._$AH,n=t===M&&i!==M||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==M&&(i===M||n);n&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}}class Z{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){B(this,t)}}const F=window.litHtmlPolyfillSupport;var G,Q;null==F||F(z,D),(null!==(v=globalThis.litHtmlVersions)&&void 0!==v?v:globalThis.litHtmlVersions=[]).push("2.1.2");class X extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,s)=>{var i,n;const r=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let l=r._$litPart$;if(void 0===l){const t=null!==(n=null==s?void 0:s.renderBefore)&&void 0!==n?n:null;r._$litPart$=l=new D(e.insertBefore(A(),t),t,void 0,null!=s?s:{})}return l._$AI(t),l})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return N}}X.finalized=!0,X._$litElement$=!0,null===(G=globalThis.litElementHydrateSupport)||void 0===G||G.call(globalThis,{LitElement:X});const Y=globalThis.litElementPolyfillSupport;null==Y||Y({LitElement:X}),(null!==(Q=globalThis.litElementVersions)&&void 0!==Q?Q:globalThis.litElementVersions=[]).push("3.0.2");class tt extends X{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(){const t=document.getElementById(this.tabname);this.visible=t.classList.contains("active")}connectedCallback(){super.connectedCallback(),window.addEventListener("click",this._handleClick),this.checkVisible()}disconnectedCallback(){window.removeEventListener("click",this._handleClick),super.disconnectedCallback()}constructor(){super(),this._handleClick=this.checkVisible.bind(this)}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return this.visible?H`${this.visibleTemplate()}`:H``}}customElements.define("wult-tab",tt);class et extends X{static styles=r`
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
  `;static properties={path:{type:String}};render(){return H`
            <div class="plot">
                <iframe seamless="seamless" frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
            </div>
        `}}customElements.define("diagram-element",et);class st extends X{static styles=r`
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
    `;getWidth(t){const e=Object.keys(t).length;return Math.min(100,20*e)}}customElements.define("report-table",st),customElements.define("smry-tbl",class extends st{static properties={smrystbl:{type:Object}};headerTemplate(){return H`
            <tr>
                ${Object.keys(this.smrystbl).map((t=>{let e;return e="Title"===t?2:"",H`<th colspan="${e}">${t}</th>`}))}
            </tr>
        `}rowsTemplate(){return H`
            ${Object.entries(this.smrystbl.Title).map((([t,e])=>Object.entries(e.funcs).map((([s,i],n)=>H`<tr>
                        ${n?H``:H`
                            <td class="td-colname" rowspan="${Object.keys(e.funcs).length}">
                                <abbr title="${e.coldescr}">${e.metric}</abbr>
                            </td>
                        `}
                        <td class="td-funcname">
                            <abbr title="${i}">${s}</abbr>
                        </td>
                        ${Object.entries(this.smrystbl).map((([e,i])=>{if("Title"===e)return H``;const n=i[t].funcs[s];return H`
                            <td class="td-value">
                                <abbr title="${n.hovertext}">${n.val}</abbr>
                            </td>
                            `}))}
                    </tr>
                    `))))}
        `}render(){return this.smrystbl?H`
            <table width="${this.getWidth(this.smrystbl)}%">
            ${this.headerTemplate()}
            ${this.rowsTemplate()}
            </table>
        `:H``}});class it extends tt{static styles=r`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;connectedCallback(){super.connectedCallback(),this.paths=this.info.ppaths,this.smrystbl=this.info.smrys_tbl}visibleTemplate(){return H`
            <br>
            <smry-tbl .smrystbl="${this.smrystbl}"></smry-tbl>
            <div class="grid">
            ${this.paths.map((t=>H`<diagram-element path="${t}" ></diagram-element>`))}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",it),customElements.define("intro-tbl",class extends st{static properties={introtbl:{type:Object}};connectedCallback(){super.connectedCallback(),this.link_keys=this.introtbl.link_keys,delete this.introtbl.link_keys}render(){return this.introtbl?H`
            <table width="${this.getWidth(this.introtbl)}%">
            <tr>
            ${Object.keys(this.introtbl).map((t=>H`<th>${t} </th>`))}
            </tr>
            ${Object.entries(this.introtbl.Title).map((([t,e])=>H`
                <tr>
                <td class="td-colname"> ${e} </td>
                ${Object.entries(this.introtbl).map((([s,i])=>"Title"!==s?H`<td class="td-value"> ${this.link_keys.includes(t)?i[t]?H`<a href=${i[t]}> ${e} </a>`:"Not available":i[t]} </td>`:H``))}
                </tr>
                `))}
            </table>
        `:H``}});class nt extends tt{static styles=r`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
    `;connectedCallback(){super.connectedCallback(),this.paths=this.info.ppaths,this.smrystbl=this.info.smrys_tbl}visibleTemplate(){return H`
        <br>
        <wult-metric-smry-tbl .smrystbl="${this.smrystbl}"></wult-metric-smry-tbl>
        <div class="grid">
        ${this.paths.map((t=>H`<diagram-element path="${t}" ></diagram-element>`))}
        </div>
        `}}customElements.define("stats-tab",nt)})();