// Tag premium do Ateliê. Layout 850x500, proporção real 85x50mm.
(()=>{'use strict';
const node=document.getElementById('tag-data');if(!node)return;
const data=JSON.parse(node.textContent);
const palette={
familia:{paper:'#FAFAF2',wine:'#365541',gold:'#B69A69',floral:'#819C80',name:'NATAL EM FAMÍLIA',flower:'folha'},
amor:{paper:'#FFF9F0',wine:'#601831',gold:'#B98B63',floral:'#A64D60',name:'NATAL DE QUEM AMA',flower:'rosa'},
gratidao:{paper:'#FFF9F3',wine:'#97555C',gold:'#C49D6A',floral:'#DDA9A7',name:'VOCÊ É MEU PRESENTE',flower:'flor'}
};
const p=palette[data.theme]||palette.amor;
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const wrap=(text,maxLines=3,limit=29)=>{const words=String(text).trim().split(/\s+/),out=[];let line='';for(const w of words){if(line&&(line+' '+w).length>limit){out.push(line);line=w}else line=line?line+' '+w:w}if(line)out.push(line);if(out.length>maxLines){out[maxLines-1]=out.slice(maxLines-1).join(' ');out.length=maxLines}return out};
const name=esc(data.recipient.length>22?data.recipient.slice(0,21)+'…':data.recipient);
const sender=esc(data.sender.length>22?data.sender.slice(0,21)+'…':data.sender);
const lines=wrap(data.teaser||'Existe uma surpresa esperando por você…');
const phr=lines.map((t,i)=>'<tspan x="208" dy="'+(i?34:0)+'">'+esc(t)+'</tspan>').join('');
let flora='<path d="M124 425 Q45 320 126 110" fill="none" stroke="'+p.gold+'" stroke-width="2.5"/>';
for(let i=0;i<6;i++){const y=150+i*48,x=100+(i%2)*27;flora+='<ellipse cx="'+x+'" cy="'+y+'" rx="11" ry="30" transform="rotate('+(i%2?45:-42)+' '+x+' '+y+')" fill="'+p.floral+'" opacity="'+(0.36+i*.08)+'"/>'}
if(p.flower==='rosa')flora+='<circle cx="135" cy="346" r="32" fill="'+p.floral+'"/><path d="M115 345Q104 315 139 323Q158 325 151 347Q140 366 124 346Q119 330 143 337" fill="none" stroke="'+p.wine+'" stroke-width="4"/>';
if(p.flower==='flor')flora+='<g transform="translate(138 346)">'+[0,72,144,216,288].map(a=>'<ellipse cy="-23" rx="18" ry="34" transform="rotate('+a+')" fill="'+p.floral+'"/>').join('')+'<circle r="12" fill="'+p.gold+'"/></g>';
if(p.flower==='folha')flora+='<path d="M135 386Q90 340 132 304Q171 337 135 386" fill="'+p.floral+'"/><path d="M135 386L132 313" stroke="'+p.paper+'" stroke-width="3"/>';
const qr='/qr/'+encodeURIComponent(data.id)+'.png';
const svg='<svg class="premium-svg" id="premium-art" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 850 500" role="img" aria-label="Cartão premium para '+name+'">'+
'<defs><clipPath id="tag-cut"><path d="M85 14H815Q839 14 839 39V460Q839 486 815 486H85Q65 486 53 469L13 265Q10 250 13 235L53 31Q65 14 85 14Z"/></clipPath></defs>'+
'<path d="M85 14H815Q839 14 839 39V460Q839 486 815 486H85Q65 486 53 469L13 265Q10 250 13 235L53 31Q65 14 85 14Z" fill="'+p.paper+'"/>'+
'<path d="M86 25H813Q829 25 829 42V460Q829 475 813 475H86Q74 475 65 456L24 264Q22 250 24 236L65 44Q74 25 86 25Z" stroke="'+p.gold+'" stroke-width="2.5" fill="none"/>'+
'<g clip-path="url(#tag-cut)">'+flora+'</g>'+
'<circle cx="65" cy="250" r="18" fill="'+p.gold+'"/><circle cx="65" cy="250" r="12" fill="#51474B"/>'+
'<text x="207" y="84" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="2.5" fill="'+p.wine+'">'+p.name+'</text>'+
'<path d="M207 107H326" stroke="'+p.gold+'" stroke-width="2"/><text x="333" y="113" font-family="Georgia,serif" font-size="18" fill="'+p.wine+'">♥</text><path d="M361 107H492" stroke="'+p.gold+'" stroke-width="2"/>'+
'<text x="207" y="171" font-family="Georgia,serif" font-size="26" fill="'+p.wine+'">Para: <tspan font-style="italic" font-size="'+(name.length>15?31:42)+'">'+name+'</tspan></text>'+
'<text x="208" y="'+(lines.length===1?265:lines.length===2?244:225)+'" font-family="Georgia,serif" font-size="'+(data.teaser.length>72?23:29)+'" font-style="italic" fill="'+p.wine+'">'+phr+'</text>'+
'<text x="207" y="376" font-family="Georgia,serif" font-size="24" fill="'+p.wine+'">De: <tspan font-style="italic" font-size="36">'+sender+'</tspan></text>'+
'<text x="207" y="423" font-family="Arial,sans-serif" font-size="13" letter-spacing=".6" fill="'+p.wine+'">APONTE A CÂMERA PARA O QR CODE →</text>'+
'<path d="M550 65V436" stroke="'+p.gold+'" stroke-width="1.7"/>'+
'<rect x="579" y="117" width="239" height="239" rx="4" fill="#fff" stroke="'+p.gold+'" stroke-width="2"/>'+
'<image x="589" y="127" width="219" height="219" xlink:href="'+qr+'" href="'+qr+'"/>'+
'<text x="698" y="411" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" letter-spacing="1" fill="'+p.wine+'">UMA SURPRESA PARA VOCÊ</text></svg>';
document.getElementById('premium-mount').innerHTML=svg;
const print=document.getElementById('premium-print');if(print)print.addEventListener('click',()=>window.print());
const dl=document.getElementById('premium-svg-download');if(dl)dl.addEventListener('click',async()=>{
const result=await fetch(qr,{credentials:'same-origin'});if(!result.ok)throw new Error('Não foi possível carregar o QR');
const blob=await result.blob();const base64=await new Promise((ok,fail)=>{const r=new FileReader();r.onload=()=>ok(r.result);r.onerror=fail;r.readAsDataURL(blob)});
const clone=document.getElementById('premium-art').cloneNode(true);const img=clone.querySelector('image');img.setAttribute('href',base64);img.setAttributeNS('http://www.w3.org/1999/xlink','xlink:href',base64);
clone.setAttribute('width','85mm');clone.setAttribute('height','50mm');
const file=new Blob([new XMLSerializer().serializeToString(clone)],{type:'image/svg+xml;charset=utf-8'});const url=URL.createObjectURL(file);const a=document.createElement('a');a.href=url;a.download='presente-vivo-'+data.id+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),3000);
});
})();