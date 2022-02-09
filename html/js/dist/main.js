/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e=Symbol(),s=new Map;class i{constructor(t,s){if(this._$cssResult$=!0,s!==e)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let e=s.get(this.cssText);return t&&void 0===e&&(s.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const o=t=>new i("string"==typeof t?t:t+"",e),r=(t,...s)=>{const o=1===t.length?t[0]:s.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new i(o,e)},n=t?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return o(e)})(t):t;var l;const a=window.trustedTypes,h=a?a.emptyScript:"",c=window.reactiveElementPolyfillSupport,d={toAttribute(t,e){switch(e){case Boolean:t=t?h:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},p=(t,e)=>e!==t&&(e==e||t==t),u={attribute:!0,type:String,converter:d,reflect:!1,hasChanged:p};class v extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=u){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const o=this[t];this[e]=i,this.requestUpdate(t,o,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||u}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var e;const s=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{t?e.adoptedStyleSheets=s.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):s.forEach((t=>{const s=document.createElement("style"),i=window.litNonce;void 0!==i&&s.setAttribute("nonce",i),s.textContent=t.cssText,e.appendChild(s)}))})(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=u){var i,o;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(o=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==o?o:d.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,i,o;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),l=t.converter,a=null!==(o=null!==(i=null===(s=l)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof l?l:null)&&void 0!==o?o:d.fromAttribute;this._$Ei=n,this[n]=a(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}}var b;v.finalized=!0,v.elementProperties=new Map,v.elementStyles=[],v.shadowRootOptions={mode:"open"},null==c||c({ReactiveElement:v}),(null!==(l=globalThis.reactiveElementVersions)&&void 0!==l?l:globalThis.reactiveElementVersions=[]).push("1.2.1");const g=globalThis.trustedTypes,m=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,f=`lit$${(Math.random()+"").slice(9)}$`,$="?"+f,_=`<${$}>`,y=document,w=(t="")=>y.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,E=Array.isArray,S=t=>{var e;return E(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])},x=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,C=/-->/g,T=/>/g,k=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,U=/'/g,P=/"/g,O=/^(?:script|style|textarea)$/i,M=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),z=M(1),H=(M(2),Symbol.for("lit-noChange")),N=Symbol.for("lit-nothing"),R=new WeakMap,L=(t,e,s)=>{var i,o;const r=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=r._$litPart$;if(void 0===n){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;r._$litPart$=n=new V(e.insertBefore(w(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n},B=y.createTreeWalker(y,129,null,!1),I=(t,e)=>{const s=t.length-1,i=[];let o,r=2===e?"<svg>":"",n=x;for(let e=0;e<s;e++){const s=t[e];let l,a,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,a=n.exec(s),null!==a);)c=n.lastIndex,n===x?"!--"===a[1]?n=C:void 0!==a[1]?n=T:void 0!==a[2]?(O.test(a[2])&&(o=RegExp("</"+a[2],"g")),n=k):void 0!==a[3]&&(n=k):n===k?">"===a[0]?(n=null!=o?o:x,h=-1):void 0===a[1]?h=-2:(h=n.lastIndex-a[2].length,l=a[1],n=void 0===a[3]?k:'"'===a[3]?P:U):n===P||n===U?n=k:n===C||n===T?n=x:(n=k,o=void 0);const d=n===k&&t[e+1].startsWith("/>")?" ":"";r+=n===x?s+_:h>=0?(i.push(l),s.slice(0,h)+"$lit$"+s.slice(h)+f+d):s+f+(-2===h?(i.push(void 0),e):d)}const l=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==m?m.createHTML(l):l,i]};class j{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,r=0;const n=t.length-1,l=this.parts,[a,h]=I(t,e);if(this.el=j.createElement(a,s),B.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=B.nextNode())&&l.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(f)){const s=h[r++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(f),e=/([.?@])?(.*)/.exec(s);l.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?F:"?"===e[1]?J:"@"===e[1]?Z:q})}else l.push({type:6,index:o})}for(const e of t)i.removeAttribute(e)}if(O.test(i.tagName)){const t=i.textContent.split(f),e=t.length-1;if(e>0){i.textContent=g?g.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],w()),B.nextNode(),l.push({type:2,index:++o});i.append(t[e],w())}}}else if(8===i.nodeType)if(i.data===$)l.push({type:2,index:o});else{let t=-1;for(;-1!==(t=i.data.indexOf(f,t+1));)l.push({type:7,index:o}),t+=f.length-1}o++}}static createElement(t,e){const s=y.createElement("template");return s.innerHTML=t,s}}function D(t,e,s=t,i){var o,r,n,l;if(e===H)return e;let a=void 0!==i?null===(o=s._$Cl)||void 0===o?void 0:o[i]:s._$Cu;const h=A(e)?void 0:e._$litDirective$;return(null==a?void 0:a.constructor)!==h&&(null===(r=null==a?void 0:a._$AO)||void 0===r||r.call(a,!1),void 0===h?a=void 0:(a=new h(t),a._$AT(t,s,i)),void 0!==i?(null!==(n=(l=s)._$Cl)&&void 0!==n?n:l._$Cl=[])[i]=a:s._$Cu=a),void 0!==a&&(e=D(t,a._$AS(t,e.values),a,i)),e}class W{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:y).importNode(s,!0);B.currentNode=o;let r=B.nextNode(),n=0,l=0,a=i[0];for(;void 0!==a;){if(n===a.index){let e;2===a.type?e=new V(r,r.nextSibling,this,t):1===a.type?e=new a.ctor(r,a.name,a.strings,this,t):6===a.type&&(e=new G(r,this,t)),this.v.push(e),a=i[++l]}n!==(null==a?void 0:a.index)&&(r=B.nextNode(),n++)}return o}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class V{constructor(t,e,s,i){var o;this.type=2,this._$AH=N,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(o=null==i?void 0:i.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=D(this,t,e),A(t)?t===N||null==t||""===t?(this._$AH!==N&&this._$AR(),this._$AH=N):t!==this._$AH&&t!==H&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):S(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==N&&A(this._$AH)?this._$AA.nextSibling.data=t:this.S(y.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,o="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=j.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(s);else{const t=new W(o,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=R.get(t.strings);return void 0===e&&R.set(t.strings,e=new j(t)),e}A(t){E(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const o of t)i===e.length?e.push(s=new V(this.M(w()),this.M(w()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class q{constructor(t,e,s,i,o){this.type=1,this._$AH=N,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=N}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const o=this.strings;let r=!1;if(void 0===o)t=D(this,t,e,0),r=!A(t)||t!==this._$AH&&t!==H,r&&(this._$AH=t);else{const i=t;let n,l;for(t=o[0],n=0;n<o.length-1;n++)l=D(this,i[s+n],e,n),l===H&&(l=this._$AH[n]),r||(r=!A(l)||l!==this._$AH[n]),l===N?t=N:t!==N&&(t+=(null!=l?l:"")+o[n+1]),this._$AH[n]=l}r&&!i&&this.k(t)}k(t){t===N?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class F extends q{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===N?void 0:t}}const K=g?g.emptyScript:"";class J extends q{constructor(){super(...arguments),this.type=4}k(t){t&&t!==N?this.element.setAttribute(this.name,K):this.element.removeAttribute(this.name)}}class Z extends q{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=D(this,t,e,0))&&void 0!==s?s:N)===H)return;const i=this._$AH,o=t===N&&i!==N||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==N&&(i===N||o);o&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}}class G{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){D(this,t)}}const Q={P:"$lit$",V:f,L:$,I:1,N:I,R:W,D:S,j:D,H:V,O:q,F:J,B:Z,W:F,Z:G},X=window.litHtmlPolyfillSupport;var Y,tt;null==X||X(j,V),(null!==(b=globalThis.litHtmlVersions)&&void 0!==b?b:globalThis.litHtmlVersions=[]).push("2.1.2");class et extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=L(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return H}}et.finalized=!0,et._$litElement$=!0,null===(Y=globalThis.litElementHydrateSupport)||void 0===Y||Y.call(globalThis,{LitElement:et});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:et}),(null!==(tt=globalThis.litElementVersions)&&void 0!==tt?tt:globalThis.litElementVersions=[]).push("3.1.2");class it extends et{static styles=r`
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
    `;getWidth(t){const e=Object.keys(t).length;return Math.min(100,20*e)}}var ot;customElements.define("report-table",it),customElements.define("intro-tbl",class extends it{static properties={introtbl:{type:Object}};connectedCallback(){super.connectedCallback(),this.link_keys=this.introtbl.link_keys,delete this.introtbl.link_keys}render(){return this.introtbl?z`
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
        `:z``}});var rt=globalThis.trustedTypes,nt=rt?rt.createPolicy("lit-html",{createHTML:t=>t}):void 0,lt=`lit$${(Math.random()+"").slice(9)}$`,at="?"+lt,ht=`<${at}>`,ct=document,dt=(t="")=>ct.createComment(t),pt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,ut=Array.isArray,vt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,bt=/-->/g,gt=/>/g,mt=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,ft=/'/g,$t=/"/g,_t=/^(?:script|style|textarea)$/i,yt=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),wt=yt(1),At=(yt(2),Symbol.for("lit-noChange")),Et=Symbol.for("lit-nothing"),St=new WeakMap,xt=ct.createTreeWalker(ct,129,null,!1),Ct=class{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,r=0;const n=t.length-1,l=this.parts,[a,h]=((t,e)=>{const s=t.length-1,i=[];let o,r=2===e?"<svg>":"",n=vt;for(let e=0;e<s;e++){const s=t[e];let l,a,h=-1,c=0;for(;c<s.length&&(n.lastIndex=c,a=n.exec(s),null!==a);)c=n.lastIndex,n===vt?"!--"===a[1]?n=bt:void 0!==a[1]?n=gt:void 0!==a[2]?(_t.test(a[2])&&(o=RegExp("</"+a[2],"g")),n=mt):void 0!==a[3]&&(n=mt):n===mt?">"===a[0]?(n=null!=o?o:vt,h=-1):void 0===a[1]?h=-2:(h=n.lastIndex-a[2].length,l=a[1],n=void 0===a[3]?mt:'"'===a[3]?$t:ft):n===$t||n===ft?n=mt:n===bt||n===gt?n=vt:(n=mt,o=void 0);const d=n===mt&&t[e+1].startsWith("/>")?" ":"";r+=n===vt?s+ht:h>=0?(i.push(l),s.slice(0,h)+"$lit$"+s.slice(h)+lt+d):s+lt+(-2===h?(i.push(void 0),e):d)}const l=r+(t[s]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==nt?nt.createHTML(l):l,i]})(t,e);if(this.el=Ct.createElement(a,s),xt.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(i=xt.nextNode())&&l.length<n;){if(1===i.nodeType){if(i.hasAttributes()){const t=[];for(const e of i.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(lt)){const s=h[r++];if(t.push(e),void 0!==s){const t=i.getAttribute(s.toLowerCase()+"$lit$").split(lt),e=/([.?@])?(.*)/.exec(s);l.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?Pt:"?"===e[1]?Mt:"@"===e[1]?zt:Ut})}else l.push({type:6,index:o})}for(const e of t)i.removeAttribute(e)}if(_t.test(i.tagName)){const t=i.textContent.split(lt),e=t.length-1;if(e>0){i.textContent=rt?rt.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],dt()),xt.nextNode(),l.push({type:2,index:++o});i.append(t[e],dt())}}}else if(8===i.nodeType)if(i.data===at)l.push({type:2,index:o});else{let t=-1;for(;-1!==(t=i.data.indexOf(lt,t+1));)l.push({type:7,index:o}),t+=lt.length-1}o++}}static createElement(t,e){const s=ct.createElement("template");return s.innerHTML=t,s}};function Tt(t,e,s=t,i){var o,r,n,l;if(e===At)return e;let a=void 0!==i?null===(o=s._$Cl)||void 0===o?void 0:o[i]:s._$Cu;const h=pt(e)?void 0:e._$litDirective$;return(null==a?void 0:a.constructor)!==h&&(null===(r=null==a?void 0:a._$AO)||void 0===r||r.call(a,!1),void 0===h?a=void 0:(a=new h(t),a._$AT(t,s,i)),void 0!==i?(null!==(n=(l=s)._$Cl)&&void 0!==n?n:l._$Cl=[])[i]=a:s._$Cu=a),void 0!==a&&(e=Tt(t,a._$AS(t,e.values),a,i)),e}var kt=class{constructor(t,e,s,i){var o;this.type=2,this._$AH=Et,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cg=null===(o=null==i?void 0:i.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Tt(this,t,e),pt(t)?t===Et||null==t||""===t?(this._$AH!==Et&&this._$AR(),this._$AH=Et):t!==this._$AH&&t!==At&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):(t=>{var e;return ut(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.A(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==Et&&pt(this._$AH)?this._$AA.nextSibling.data=t:this.S(ct.createTextNode(t)),this._$AH=t}T(t){var e;const{values:s,_$litType$:i}=t,o="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Ct.createElement(i.h,this.options)),i);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(s);else{const t=new class{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:s},parts:i}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:ct).importNode(s,!0);xt.currentNode=o;let r=xt.nextNode(),n=0,l=0,a=i[0];for(;void 0!==a;){if(n===a.index){let e;2===a.type?e=new kt(r,r.nextSibling,this,t):1===a.type?e=new a.ctor(r,a.name,a.strings,this,t):6===a.type&&(e=new Ht(r,this,t)),this.v.push(e),a=i[++l]}n!==(null==a?void 0:a.index)&&(r=xt.nextNode(),n++)}return o}m(t){let e=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}(o,this),e=t.p(this.options);t.m(s),this.S(e),this._$AH=t}}_$AC(t){let e=St.get(t.strings);return void 0===e&&St.set(t.strings,e=new Ct(t)),e}A(t){ut(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const o of t)i===e.length?e.push(s=new kt(this.M(dt()),this.M(dt()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Ut=class{constructor(t,e,s,i,o){this.type=1,this._$AH=Et,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=Et}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,s,i){const o=this.strings;let r=!1;if(void 0===o)t=Tt(this,t,e,0),r=!pt(t)||t!==this._$AH&&t!==At,r&&(this._$AH=t);else{const i=t;let n,l;for(t=o[0],n=0;n<o.length-1;n++)l=Tt(this,i[s+n],e,n),l===At&&(l=this._$AH[n]),r||(r=!pt(l)||l!==this._$AH[n]),l===Et?t=Et:t!==Et&&(t+=(null!=l?l:"")+o[n+1]),this._$AH[n]=l}r&&!i&&this.k(t)}k(t){t===Et?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Pt=class extends Ut{constructor(){super(...arguments),this.type=3}k(t){this.element[this.name]=t===Et?void 0:t}},Ot=rt?rt.emptyScript:"",Mt=class extends Ut{constructor(){super(...arguments),this.type=4}k(t){t&&t!==Et?this.element.setAttribute(this.name,Ot):this.element.removeAttribute(this.name)}},zt=class extends Ut{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){var s;if((t=null!==(s=Tt(this,t,e,0))&&void 0!==s?s:Et)===At)return;const i=this._$AH,o=t===Et&&i!==Et||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==Et&&(i===Et||o);o&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t)}},Ht=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){Tt(this,t)}},Nt=window.litHtmlPolyfillSupport;null==Nt||Nt(Ct,kt),(null!==(ot=globalThis.litHtmlVersions)&&void 0!==ot?ot:globalThis.litHtmlVersions=[]).push("2.1.0");var Rt,Lt,Bt,It=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,jt=Symbol(),Dt=new Map,Wt=class{constructor(t,e){if(this._$cssResult$=!0,e!==jt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=Dt.get(this.cssText);return It&&void 0===t&&(Dt.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}},Vt=t=>new Wt("string"==typeof t?t:t+"",jt),qt=(t,...e)=>{const s=1===t.length?t[0]:e.reduce(((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1]),t[0]);return new Wt(s,jt)},Ft=It?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return Vt(e)})(t):t,Kt=window.trustedTypes,Jt=Kt?Kt.emptyScript:"",Zt=window.reactiveElementPolyfillSupport,Gt={toAttribute(t,e){switch(e){case Boolean:t=t?Jt:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},Qt=(t,e)=>e!==t&&(e==e||t==t),Xt={attribute:!0,type:String,converter:Gt,reflect:!1,hasChanged:Qt},Yt=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=Xt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const o=this[t];this[e]=i,this.requestUpdate(t,o,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Xt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(Ft(t))}else void 0!==t&&e.push(Ft(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,It?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=Xt){var i,o;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(o=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==o?o:Gt.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,i,o;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),l=t.converter,a=null!==(o=null!==(i=null===(s=l)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof l?l:null)&&void 0!==o?o:Gt.fromAttribute;this._$Ei=n,this[n]=a(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||Qt)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}};Yt.finalized=!0,Yt.elementProperties=new Map,Yt.elementStyles=[],Yt.shadowRootOptions={mode:"open"},null==Zt||Zt({ReactiveElement:Yt}),(null!==(Rt=globalThis.reactiveElementVersions)&&void 0!==Rt?Rt:globalThis.reactiveElementVersions=[]).push("1.1.0");var te=class extends Yt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const s=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=s.firstChild),s}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,s)=>{var i,o;const r=null!==(i=null==s?void 0:s.renderBefore)&&void 0!==i?i:e;let n=r._$litPart$;if(void 0===n){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;r._$litPart$=n=new kt(e.insertBefore(dt(),t),t,void 0,null!=s?s:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return At}};te.finalized=!0,te._$litElement$=!0,null===(Lt=globalThis.litElementHydrateSupport)||void 0===Lt||Lt.call(globalThis,{LitElement:te});var ee=globalThis.litElementPolyfillSupport;null==ee||ee({LitElement:te}),(null!==(Bt=globalThis.litElementVersions)&&void 0!==Bt?Bt:globalThis.litElementVersions=[]).push("3.1.0");var se,ie=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,oe=Symbol(),re=new Map,ne=t=>new class{constructor(t,e){if(this._$cssResult$=!0,e!==oe)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=re.get(this.cssText);return ie&&void 0===t&&(re.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}}("string"==typeof t?t:t+"",oe),le=ie?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return ne(e)})(t):t,ae=window.trustedTypes,he=ae?ae.emptyScript:"",ce=window.reactiveElementPolyfillSupport,de={toAttribute(t,e){switch(e){case Boolean:t=t?he:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},pe=(t,e)=>e!==t&&(e==e||t==t),ue={attribute:!0,type:String,converter:de,reflect:!1,hasChanged:pe},ve=class extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,s)=>{const i=this._$Eh(s,e);void 0!==i&&(this._$Eu.set(i,s),t.push(i))})),t}static createProperty(t,e=ue){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,s,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){return{get(){return this[e]},set(i){const o=this[t];this[e]=i,this.requestUpdate(t,o,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||ue}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of e)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(le(t))}else void 0!==t&&e.push(le(t));return e}static _$Eh(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,s;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return s=e,i=this.constructor.elementStyles,ie?s.adoptedStyleSheets=i.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):i.forEach((t=>{const e=document.createElement("style"),i=window.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=t.cssText,s.appendChild(e)})),e;var s,i}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ES(t,e,s=ue){var i,o;const r=this.constructor._$Eh(t,s);if(void 0!==r&&!0===s.reflect){const n=(null!==(o=null===(i=s.converter)||void 0===i?void 0:i.toAttribute)&&void 0!==o?o:de.toAttribute)(e,s.type);this._$Ei=t,null==n?this.removeAttribute(r):this.setAttribute(r,n),this._$Ei=null}}_$AK(t,e){var s,i,o;const r=this.constructor,n=r._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=r.getPropertyOptions(n),l=t.converter,a=null!==(o=null!==(i=null===(s=l)||void 0===s?void 0:s.fromAttribute)&&void 0!==i?i:"function"==typeof l?l:null)&&void 0!==o?o:de.fromAttribute;this._$Ei=n,this[n]=a(e,t.type),this._$Ei=null}}requestUpdate(t,e,s){let i=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||pe)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$E_&&(this._$E_=new Map),this._$E_.set(t,s))):i=!1),!this.isUpdatePending&&i&&(this._$Ep=this._$EC())}async _$EC(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const s=this._$AL;try{e=this.shouldUpdate(s),e?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(s)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(s)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$E_&&(this._$E_.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$E_=void 0),this._$EU()}updated(t){}firstUpdated(t){}};ve.finalized=!0,ve.elementProperties=new Map,ve.elementStyles=[],ve.shadowRootOptions={mode:"open"},null==ce||ce({ReactiveElement:ve}),(null!==(se=globalThis.reactiveElementVersions)&&void 0!==se?se:globalThis.reactiveElementVersions=[]).push("1.1.0");var be=qt`
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
`,ge=qt`
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
`,me=document.createElement("style");me.textContent=be.toString(),document.head.append(me);var fe,$e=qt`
  ${ge}

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
`,_e=new Set,ye=new MutationObserver(Ee),we=new Map,Ae=document.documentElement.lang||navigator.language;function Ee(){Ae=document.documentElement.lang||navigator.language,[..._e.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}ye.observe(document.documentElement,{attributes:!0,attributeFilter:["lang"]});var Se=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){_e.add(this.host)}hostDisconnected(){_e.delete(this.host)}term(t,...e){return function(t,e,...s){const i=t.toLowerCase().slice(0,2),o=t.length>2?t.toLowerCase():"",r=we.get(o),n=we.get(i);let l;if(r&&r[e])l=r[e];else if(n&&n[e])l=n[e];else{if(!fe||!fe[e])return console.error(`No translation found for: ${e}`),e;l=fe[e]}return"function"==typeof l?l(...s):l}(this.host.lang||Ae,t,...e)}date(t,e){return function(t,e,s){return e=new Date(e),new Intl.DateTimeFormat(t,s).format(e)}(this.host.lang||Ae,t,e)}number(t,e){return function(t,e,s){return e=Number(e),isNaN(e)?"":new Intl.NumberFormat(t,s).format(e)}(this.host.lang||Ae,t,e)}relativeTime(t,e,s){return function(t,e,s,i){return new Intl.RelativeTimeFormat(t,i).format(e,s)}(this.host.lang||Ae,t,e,s)}};function xe(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}function Ce(t,e,s="vertical",i="smooth"){const o=xe(t,e),r=o.top+e.scrollTop,n=o.left+e.scrollLeft,l=e.scrollLeft,a=e.scrollLeft+e.offsetWidth,h=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==s&&"both"!==s||(n<l?e.scrollTo({left:n,behavior:i}):n+t.clientWidth>a&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:i})),"vertical"!==s&&"both"!==s||(r<h?e.scrollTo({top:r,behavior:i}):r+t.clientHeight>c&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:i}))}!function(...t){t.map((t=>{const e=t.$code.toLowerCase();we.set(e,t),fe||(fe=t)})),Ee()}({$code:"en",$name:"English",$dir:"ltr",close:"Close",copy:"Copy",progress:"Progress",resize:"Resize",scroll_to_end:"Scroll to end",scroll_to_start:"Scroll to start",select_a_color_from_the_screen:"Select a color from the screen",toggle_color_format:"Toggle color format"});var Te=t=>(...e)=>({_$litDirective$:t,values:e}),ke=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},Ue=Te(class extends ke{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var s,i;if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.et=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(s=this.et)||void 0===s?void 0:s.has(t))&&this.st.add(t);return this.render(e)}const o=t.element.classList;this.st.forEach((t=>{t in e||(o.remove(t),this.st.delete(t))}));for(const t in e){const s=!!e[t];s===this.st.has(t)||(null===(i=this.et)||void 0===i?void 0:i.has(t))||(s?(o.add(t),this.st.add(t)):(o.remove(t),this.st.delete(t)))}return At}});function Pe(t,e){return(s,i)=>{const{update:o}=s;e=Object.assign({waitUntilFirstUpdate:!1},e),s.update=function(s){if(s.has(t)){const o=s.get(t),r=this[t];o!==r&&((null==e?void 0:e.waitUntilFirstUpdate)&&!this.hasUpdated||this[i].call(this,o,r))}o.call(this,s)}}}function Oe(t,e,s){const i=new CustomEvent(e,Object.assign({bubbles:!0,cancelable:!1,composed:!0,detail:{}},s));return t.dispatchEvent(i),i}Object.create;var Me=Object.defineProperty,ze=Object.defineProperties,He=Object.getOwnPropertyDescriptor,Ne=Object.getOwnPropertyDescriptors,Re=(Object.getOwnPropertyNames,Object.getOwnPropertySymbols),Le=(Object.getPrototypeOf,Object.prototype.hasOwnProperty),Be=Object.prototype.propertyIsEnumerable,Ie=(t,e,s)=>e in t?Me(t,e,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[e]=s,je=(t,e)=>{for(var s in e||(e={}))Le.call(e,s)&&Ie(t,s,e[s]);if(Re)for(var s of Re(e))Be.call(e,s)&&Ie(t,s,e[s]);return t},De=(t,e)=>ze(t,Ne(e)),We=(t,e,s,i)=>{for(var o,r=i>1?void 0:i?He(e,s):e,n=t.length-1;n>=0;n--)(o=t[n])&&(r=(i?o(e,s,r):o(r))||r);return i&&r&&Me(e,s,r),r},Ve=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:s,elements:i}=e;return{kind:s,elements:i,finisher(e){window.customElements.define(t,e)}}})(t,e),qe=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?De(je({},e),{finisher(s){s.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(s){s.createProperty(e.key,t)}};function Fe(t){return(e,s)=>void 0!==s?((t,e,s)=>{e.constructor.createProperty(s,t)})(t,e,s):qe(t,e)}function Ke(t){return Fe(De(je({},t),{state:!0}))}function Je(t,e){return(({finisher:t,descriptor:e})=>(s,i)=>{var o;if(void 0===i){const i=null!==(o=s.originalKey)&&void 0!==o?o:s.key,r=null!=e?{kind:"method",placement:"prototype",key:i,descriptor:e(s.key)}:De(je({},s),{key:i});return null!=t&&(r.finisher=function(e){t(e,i)}),r}{const o=s.constructor;void 0!==e&&Object.defineProperty(s,i,e(i)),null==t||t(o,i)}})({descriptor:s=>{const i={get(){var e,s;return null!==(s=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==s?s:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof s?Symbol():"__"+s;i.get=function(){var s,i;return void 0===this[e]&&(this[e]=null!==(i=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(t))&&void 0!==i?i:null),this[e]}}return i}})}var Ze=class extends te{constructor(){super(...arguments),this.localize=new Se(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.preventIndicatorTransition(),this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(this.getActiveTab()||this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}getAllTabs(t=!1){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.querySelector("slot").assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=document.activeElement;if(e&&"sl-tab"===e.tagName.toLowerCase()){let s=this.tabs.indexOf(e);"Home"===t.key?s=0:"End"===t.key?s=this.tabs.length-1:["top","bottom"].includes(this.placement)&&"ArrowLeft"===t.key||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?s=Math.max(0,s-1):(["top","bottom"].includes(this.placement)&&"ArrowRight"===t.key||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&(s=Math.min(this.tabs.length-1,s+1)),this.tabs[s].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[s],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Ce(this.tabs[s],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}updateScrollControls(){this.nav&&(this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth)}setActiveTab(t,e){if(e=Object.assign({emitEvents:!0,scrollBehavior:"auto"},e),t&&t!==this.activeTab&&!t.disabled){const s=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>t.active=t.name===this.activeTab.panel)),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Ce(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(s&&Oe(this,"sl-tab-hide",{detail:{name:s.panel}}),Oe(this,"sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.map((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}syncIndicator(){if(this.indicator){if(!this.getActiveTab())return void(this.indicator.style.display="none");this.indicator.style.display="block",this.repositionIndicator()}}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,s=t.clientHeight,i=xe(t,this.nav),o=i.top+this.nav.scrollTop,r=i.left+this.nav.scrollLeft;switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.transform=`translateX(${r}px)`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${s}px`,this.indicator.style.transform=`translateY(${o}px)`}}preventIndicatorTransition(){const t=this.indicator.style.transition;this.indicator.style.transition="none",requestAnimationFrame((()=>{this.indicator.style.transition=t}))}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.panels=this.getAllPanels(),this.syncIndicator()}render(){return wt`
      <div
        part="base"
        class=${Ue({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?wt`
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

          ${this.hasScrollControls?wt`
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
    `}};Ze.styles=$e,We([Je(".tab-group")],Ze.prototype,"tabGroup",2),We([Je(".tab-group__body")],Ze.prototype,"body",2),We([Je(".tab-group__nav")],Ze.prototype,"nav",2),We([Je(".tab-group__indicator")],Ze.prototype,"indicator",2),We([Ke()],Ze.prototype,"hasScrollControls",2),We([Fe()],Ze.prototype,"placement",2),We([Fe()],Ze.prototype,"activation",2),We([Fe({attribute:"no-scroll-controls",type:Boolean})],Ze.prototype,"noScrollControls",2),We([Fe()],Ze.prototype,"lang",2),We([Pe("noScrollControls")],Ze.prototype,"updateScrollControls",1),We([Pe("placement")],Ze.prototype,"syncIndicator",1),Ze=We([Ve("sl-tab-group")],Ze);var Ge=(()=>{const t=document.createElement("style");let e;try{document.head.appendChild(t),t.sheet.insertRule(":focus-visible { color: inherit }"),e=!0}catch(t){e=!1}finally{t.remove()}return e})(),Qe=Vt(Ge?":focus-visible":":focus"),Xe=qt`
  ${ge}

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

  .icon-button${Qe} {
    box-shadow: var(--sl-focus-ring);
  }
`,Ye=t=>null!=t?t:Et,ts=class extends te{constructor(){super(...arguments),this.label="",this.disabled=!1}render(){const t=!!this.href,e=wt`
      <sl-icon
        name=${Ye(this.name)}
        library=${Ye(this.library)}
        src=${Ye(this.src)}
        aria-hidden="true"
      ></sl-icon>
    `;return t?wt`
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
        `:wt`
          <button
            part="base"
            class=${Ue({"icon-button":!0,"icon-button--disabled":this.disabled})}
            ?disabled=${this.disabled}
            type="button"
            aria-label=${this.label}
          >
            ${e}
          </button>
        `}};ts.styles=Xe,We([Je("button")],ts.prototype,"button",2),We([Fe()],ts.prototype,"name",2),We([Fe()],ts.prototype,"library",2),We([Fe()],ts.prototype,"src",2),We([Fe()],ts.prototype,"href",2),We([Fe()],ts.prototype,"target",2),We([Fe()],ts.prototype,"download",2),We([Fe()],ts.prototype,"label",2),We([Fe({type:Boolean,reflect:!0})],ts.prototype,"disabled",2),ts=We([Ve("sl-icon-button")],ts);var es="";function ss(t){es=t}var is=[...document.getElementsByTagName("script")],os=is.find((t=>t.hasAttribute("data-shoelace")));if(os)ss(os.getAttribute("data-shoelace"));else{const t=is.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let e="";t&&(e=t.getAttribute("src")),ss(e.split("/").slice(0,-1).join("/"))}var rs={check:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">\n      <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',x:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">\n      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},ns=[{name:"default",resolver:t=>`${es.replace(/\/$/,"")}/assets/icons/${t}.svg`},{name:"system",resolver:t=>rs[t]?`data:image/svg+xml,${encodeURIComponent(rs[t])}`:""}],ls=[];function as(t){return ns.filter((e=>e.name===t))[0]}var hs=new Map,cs=qt`
  ${ge}

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
`,ds=class extends ke{constructor(t){if(super(t),this.it=Et,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===Et||null==t)return this.vt=void 0,this.it=t;if(t===At)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this.vt;this.it=t;const e=[t];return e.raw=e,this.vt={_$litType$:this.constructor.resultType,strings:e,values:[]}}};ds.directiveName="unsafeHTML",ds.resultType=1,Te(ds);var ps=class extends ds{};ps.directiveName="unsafeSVG",ps.resultType=2;var us=Te(ps),vs=new DOMParser,bs=class extends te{constructor(){super(...arguments),this.svg="",this.library="default"}connectedCallback(){super.connectedCallback(),ls.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,ls=ls.filter((e=>e!==t))}getUrl(){const t=as(this.library);return this.name&&t?t.resolver(this.name):this.src}redraw(){this.setIcon()}async setIcon(){const t=as(this.library),e=this.getUrl();if(e)try{const s=await(t=>{if(hs.has(t))return hs.get(t);{const e=fetch(t).then((async t=>{if(t.ok){const e=document.createElement("div");e.innerHTML=await t.text();const s=e.firstElementChild;return{ok:t.ok,status:t.status,svg:s&&"svg"===s.tagName.toLowerCase()?s.outerHTML:""}}return{ok:t.ok,status:t.status,svg:null}}));return hs.set(t,e),e}})(e);if(e!==this.getUrl())return;if(s.ok){const e=vs.parseFromString(s.svg,"text/html").body.querySelector("svg");e?(t&&t.mutator&&t.mutator(e),this.svg=e.outerHTML,Oe(this,"sl-load")):(this.svg="",Oe(this,"sl-error",{detail:{status:s.status}}))}else this.svg="",Oe(this,"sl-error",{detail:{status:s.status}})}catch(t){Oe(this,"sl-error",{detail:{status:-1}})}else this.svg&&(this.svg="")}handleChange(){this.setIcon()}render(){const t="string"==typeof this.label&&this.label.length>0;return wt` <div
      part="base"
      class="icon"
      role=${Ye(t?"img":void 0)}
      aria-label=${Ye(t?this.label:void 0)}
      aria-hidden=${Ye(t?void 0:"true")}
    >
      ${us(this.svg)}
    </div>`}};bs.styles=cs,We([Ke()],bs.prototype,"svg",2),We([Fe()],bs.prototype,"name",2),We([Fe()],bs.prototype,"src",2),We([Fe()],bs.prototype,"label",2),We([Fe()],bs.prototype,"library",2),We([Pe("name"),Pe("src"),Pe("library")],bs.prototype,"setIcon",1),bs=We([Ve("sl-icon")],bs);var gs=qt`
  ${ge}

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

  .tab${Qe}:not(.tab--disabled) {
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
`,ms=0,fs=class extends te{constructor(){super(...arguments),this.localize=new Se(this),this.componentId="sl-tab-"+ ++ms,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}handleCloseClick(){Oe(this,"sl-close")}render(){return this.id=this.id||this.componentId,wt`
      <div
        part="base"
        class=${Ue({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        role="tab"
        aria-disabled=${this.disabled?"true":"false"}
        aria-selected=${this.active?"true":"false"}
        tabindex=${this.disabled||!this.active?"-1":"0"}
      >
        <slot></slot>
        ${this.closable?wt`
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
    `}};fs.styles=gs,We([Je(".tab")],fs.prototype,"tab",2),We([Fe({reflect:!0})],fs.prototype,"panel",2),We([Fe({type:Boolean,reflect:!0})],fs.prototype,"active",2),We([Fe({type:Boolean})],fs.prototype,"closable",2),We([Fe({type:Boolean,reflect:!0})],fs.prototype,"disabled",2),We([Fe()],fs.prototype,"lang",2),fs=We([Ve("sl-tab")],fs);var $s=qt`
  ${ge}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    border: solid 1px transparent;
    padding: var(--padding);
  }
`,_s=0,ys=class extends te{constructor(){super(...arguments),this.componentId="sl-tab-panel-"+ ++_s,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id||this.componentId}render(){return this.style.display=this.active?"block":"none",wt`
      <div part="base" class="tab-panel" role="tabpanel" aria-hidden=${this.active?"false":"true"}>
        <slot></slot>
      </div>
    `}};ys.styles=$s,We([Fe({reflect:!0})],ys.prototype,"name",2),We([Fe({type:Boolean,reflect:!0})],ys.prototype,"active",2),ys=We([Ve("sl-tab-panel")],ys);const{H:ws}=Q,As=(t,e)=>{var s,i;return void 0===e?void 0!==(null===(s=t)||void 0===s?void 0:s._$litType$):(null===(i=t)||void 0===i?void 0:i._$litType$)===e},Es=()=>document.createComment(""),Ss=(t,e,s)=>{var i;const o=t._$AA.parentNode,r=void 0===e?t._$AB:e._$AA;if(void 0===s){const e=o.insertBefore(Es(),r),i=o.insertBefore(Es(),r);s=new ws(e,i,t,t.options)}else{const e=s._$AB.nextSibling,n=s._$AM,l=n!==t;if(l){let e;null===(i=s._$AQ)||void 0===i||i.call(s,t),s._$AM=t,void 0!==s._$AP&&(e=t._$AU)!==n._$AU&&s._$AP(e)}if(e!==r||l){let t=s._$AA;for(;t!==e;){const e=t.nextSibling;o.insertBefore(t,r),t=e}}}return s},xs={},Cs=(t,e=xs)=>t._$AH=e,Ts=t=>t._$AH,ks=(Us=class extends class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}{constructor(t){super(t),this.tt=new WeakMap}render(t){return[t]}update(t,[e]){if(As(this.it)&&(!As(e)||this.it.strings!==e.strings)){const e=Ts(t).pop();let s=this.tt.get(this.it.strings);if(void 0===s){const t=document.createDocumentFragment();s=L(N,t),s.setConnected(!1),this.tt.set(this.it.strings,s)}Cs(s,[e]),Ss(s,void 0,e)}if(As(e)){if(!As(this.it)||this.it.strings!==e.strings){const s=this.tt.get(e.strings);if(void 0!==s){const e=Ts(s).pop();(t=>{t._$AR()})(t),Ss(t,void 0,e),Cs(t,[e])}}this.it=e}else this.it=void 0;return this.render(e)}},(...t)=>({_$litDirective$:Us,values:t}));var Us;class Ps extends et{static properties={tabname:{type:String},info:{type:Object},visible:{type:Boolean,attribute:!1}};checkVisible(t,e){for(const e of t)"active"===e.attributeName&&(this.tabname===e.target.id?this.visible=!0:this.visible=!1)}connectedCallback(){super.connectedCallback();const t=this.checkVisible.bind(this);this.observer=new MutationObserver(t),this.observer.observe(this.parentElement,{attributes:!0})}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}visibleTemplate(){throw new Error("Inherit from this class and implement 'visibleTemplate'.")}render(){return z`
      ${ks(this.visible?z`${this.visibleTemplate()}`:z``)}`}}customElements.define("wult-tab",Ps);class Os extends et{static styles=r`
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
        `}}customElements.define("diagram-element",Os),customElements.define("smry-tbl",class extends it{static properties={src:{type:String},template:{attribute:!1}};parseMetric(t){const e=t[0].split("|");return z`
        <td rowspan=${t[1]} class="td-colname">
            <abbr title=${e[1]}>${e[0]}</abbr>
        </td>
      `}parseSummaryFunc(t){const[e,s]=t.split("|");return z`
        <td class="td-value">
            <abbr title=${s}>${e}</abbr>
        </td>
      `}async parseSrc(){let t,e=z``;for await(const s of async function*(t){const e=new TextDecoder("utf-8"),s=(await fetch(t)).body.getReader();let{value:i,done:o}=await s.read();i=i?e.decode(i,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(i);if(t)yield i.substring(n,t.index),n=r.lastIndex;else{if(o)break;const t=i.substr(n);({value:i,done:o}=await s.read()),i=t+(i?e.decode(i,{stream:!0}):""),n=r.lastIndex=0}}n<i.length&&(yield i.substr(n))}(this.src)){const i=s.split(";"),o=i[0];if(i.shift(),"H"===o)for(const t of i)e=z`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===o)t=this.parseMetric(i);else{const s=z`
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
        `:z``}});class Ms extends Ps{static styles=r`
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
            ${this.paths.map((t=>z`<diagram-element path="${t}" ></diagram-element>`))}
            </div>
        `}render(){return super.render()}}customElements.define("wult-metric-tab",Ms);class zs extends et{static styles=r`
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
    `;static properties={tabFile:{type:String},tabs:{type:Object,attribute:!1}};connectedCallback(){super.connectedCallback(),fetch(this.tabFile).then((t=>t.json())).then((t=>{this.tabs=t}))}tabTemplate(t){return t.tabs?z`
          <sl-tab-group>
            ${t.tabs.map((t=>z`
             <sl-tab slot="nav" panel="${t.name}">${t.name}</sl-tab>
             <sl-tab-panel id="${t.name}" name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
             `))}
          </sl-tab-group>
        `:z`
      <wult-metric-tab tabname="${t.name}" .smrytblpath="${t.smrytblpath}" .paths="${t.ppaths}" .dir="${t.dir}" ></wult-metric-tab>
      `}render(){return this.tabs?z`
            <sl-tab-group>
              ${this.tabs.map((t=>z`
                  <sl-tab slot="nav" panel="${t.name}">${t.name}</sl-tab>
                  <sl-tab-panel name="${t.name}">${this.tabTemplate(t)}</sl-tab-panel>
                `))}
            </sl-tab-group>
          `:z``}}customElements.define("tab-group",zs),ss("shoelace")})();