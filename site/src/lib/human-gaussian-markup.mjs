const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const humanGaussianCopy = {
  en: {
    title:'Explore motion in 3D',
    intro:'Play the motion, pause a pose, and explore it from any angle.',
    load:'Start 3D',loading:'Loading 3D…',retry:'Try again',loadHint:'Rotate · Zoom · Play',loadError:'Could not load the 3D example. Try again.',
    observed:'Source RGB',observedBadge:'OBSERVED',reconstructed:'4D Gaussian reconstruction',inferredBadge:'INFERRED',
    emptySource:'The matching RGB video will appear here.',empty3d:'Start the 3D example to explore the motion.',
    status:'Start the example in the 3D panel.',play:'Play',pause:'Pause',seek:'Playback position',
    front:'Front',left:'Left',back:'Back',right:'Right',orbit:'Auto orbit',fit:'Fit view',close:'Close 3D',
    compare:'Compare',source:'Source only',model:'3D only',help:'Drag: orbit · Scroll/pinch: zoom · Right drag: pan. The same timeline controls both panels.',
    sourceCredit:'Source',reference:'YouTube reference',referenceTitle:'Original reference video',
    referenceText:'Watch the reference on YouTube.',
    referenceLink:'Watch the original on YouTube',referenceChannel:'지숭이_Jisoong · 체포하겠어🚨🚨',
    notice:'Side and rear appearance includes generated estimates.',
    time:'0.00 / — s',
  },
  ko: {
    title:'인체 동작을 3D로 둘러보기',
    intro:'동작을 재생하고, 한 자세에서 멈춘 뒤 여러 방향으로 돌려 보세요.',
    load:'3D 시작',loading:'3D 불러오는 중…',retry:'다시 시도',loadHint:'회전 · 확대 · 동작 재생',loadError:'3D 예제를 불러오지 못했습니다. 다시 시도해 주세요.',
    observed:'원본 RGB',observedBadge:'실제 관측',reconstructed:'인체 4D Gaussian 재구성',inferredBadge:'추정 외형 포함',
    emptySource:'대응하는 원본 RGB 영상이 여기에 표시됩니다.',empty3d:'3D를 시작하면 동작을 여러 방향에서 볼 수 있습니다.',
    status:'오른쪽 3D 화면에서 시작하세요.',play:'재생',pause:'일시 정지',seek:'재생 위치',
    front:'정면',left:'왼쪽',back:'뒤',right:'오른쪽',orbit:'자동 회전',fit:'화면에 맞추기',close:'3D 닫기',
    compare:'함께 보기',source:'원본 크게 보기',model:'3D 크게 보기',help:'드래그: 회전 · 휠/두 손가락: 확대 · 오른쪽 드래그: 이동. 아래 타임라인이 두 화면을 함께 제어합니다.',
    sourceCredit:'출처',reference:'YouTube 참고 자료',referenceTitle:'원본 참고 영상',
    referenceText:'YouTube에서 참고 영상을 확인하세요.',
    referenceLink:'YouTube에서 원본 보기',referenceChannel:'지숭이_Jisoong · 체포하겠어🚨🚨',
    notice:'옆·뒷면 외형에는 생성 모델의 추정이 포함됩니다.',
    time:'0.00 / — s',
  },
};
export function humanGaussianMarkup(locale='en',{manifestUrl='',reference=true,controlSample=false,youtubeSource=false,sourcePosterUrl='',modelPosterUrl=''}={}) {
  const ko=locale==='ko',c=humanGaussianCopy[ko?'ko':'en'];
  const sourceTitle=controlSample?(ko?'SOMA 합성 RGB · 제어 샘플':'SOMA synthetic RGB · control'):youtubeSource?(ko?'원본 YouTube':'Original YouTube'):c.observed,sourceBadge=controlSample?(ko?'합성 렌더':'SYNTHETIC RENDER'):youtubeSource?'YOUTUBE':c.observedBadge,modelTitle=controlSample?(ko?'SOMA 리깅 Gaussian 제어 샘플':'SOMA rigged Gaussian control'):c.reconstructed,modelBadge=controlSample?(ko?'알려진 리깅':'KNOWN RIG'):c.inferredBadge;
  const intro=youtubeSource?(ko?'왼쪽에서 원본을 보고, 오른쪽에서 31.9초 춤 동작을 3D로 돌려 보세요.':'Watch the original on the left and explore the 31.9-second 3D reconstruction on the right.'):c.intro;
  const help=youtubeSource?(ko?'드래그: 회전 · 휠/두 손가락: 확대 · 타임라인: 3D 재생 위치. 원본 재생은 YouTube에서 조절합니다.':'Drag to orbit · Scroll/pinch to zoom · Scrub to change 3D time. YouTube playback is controlled separately.'):c.help;
  const notice=controlSample?(ko?'SOMA의 공식 예제 동작을 Gaussian으로 표시한 합성 샘플입니다.':'A synthetic Gaussian sample driven by SOMA’s official example motion.'):c.notice;
  return `${reference&&!youtubeSource?`<section class="hg-reference" aria-label="${c.reference}"><div><span class="hg-kicker">${c.reference}</span><h3>${c.referenceTitle}</h3><p>${c.referenceText}</p><p><a href="https://www.youtube.com/shorts/rWS8uli1-m0" target="_blank" rel="noopener noreferrer">${c.referenceChannel}</a></p></div><iframe src="https://www.youtube-nocookie.com/embed/rWS8uli1-m0?playsinline=1&amp;rel=0" title="${c.referenceChannel}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></section>`:''}
  <header class="hg-heading"><h2>${c.title}</h2><p>${intro}</p></header>
  <div class="hg-display-modes" role="group" aria-label="${locale==='ko'?'비교 화면 구성':'Comparison layout'}"><button type="button" data-hg-mode="compare" aria-pressed="true">${c.compare}</button><button type="button" data-hg-mode="source" aria-pressed="false">${c.source}</button><button type="button" data-hg-mode="model" aria-pressed="false">${c.model}</button></div>
  <div class="hg-pair" data-hg-pair data-mode="compare"><section class="hg-panel hg-source-panel"><div class="hg-panel-head"><h3 data-hg-source-title>${sourceTitle}</h3><span data-hg-source-badge>${sourceBadge}</span></div><div class="hg-source-stage"><video data-hg-source ${youtubeSource?'hidden':''} muted playsinline preload="metadata" ${sourcePosterUrl?`poster="${escape(sourcePosterUrl)}"`:""} aria-label="${c.observed}"></video>${youtubeSource?`<iframe data-hg-youtube src="https://www.youtube-nocookie.com/embed/rWS8uli1-m0?playsinline=1&amp;rel=0" title="${c.referenceChannel}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>`:""}<p class="hg-empty" data-hg-source-empty ${sourcePosterUrl||youtubeSource?"hidden":""}>${c.emptySource}</p></div><p class="hg-credit" data-hg-credit>${youtubeSource?'<a href="https://www.youtube.com/shorts/rWS8uli1-m0" target="_blank" rel="noopener noreferrer">지숭이_Jisoong · 체포하겠어🚨🚨 · YouTube</a>':controlSample?'<a href="https://github.com/NVlabs/SOMA-X">NVIDIA SOMA-X</a> · Apache-2.0 · synthetic control':''}</p></section>
  <section class="hg-panel hg-model-panel"><div class="hg-panel-head"><h3 data-hg-model-title>${modelTitle}</h3><span data-hg-model-badge>${modelBadge}</span></div><div class="hg-stage" data-hg-stage>${modelPosterUrl?`<img class="hg-poster" data-hg-poster src="${escape(modelPosterUrl)}" alt="${escape(modelTitle)}" loading="lazy">`:""}<div class="hg-start-cover" data-hg-cover><div class="hg-start-card"><button type="button" data-hg-load ${manifestUrl?'':'hidden'}><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 5 9-5M12 12v10"/></svg><span data-hg-load-label>${c.load}</span></button><p data-hg-cover-message role="status" aria-live="polite">${manifestUrl?c.loadHint:c.empty3d}</p></div></div><output class="hg-view-label" data-hg-view-label>${c.front}</output></div></section></div>
  <div class="hg-controls" data-hg-controls role="group" aria-label="${ko?'3D 재생과 시점 조작':'3D playback and camera controls'}" hidden><div class="hg-timeline"><button type="button" data-hg-play disabled>${c.play}</button><output data-hg-time>${c.time}</output><input type="range" data-hg-seek min="0" max="120" step="1" value="0" aria-label="${c.seek}" disabled><button type="button" data-hg-close disabled>${c.close}</button></div><div class="hg-views" role="group" aria-label="${locale==='ko'?'3D 카메라 시점':'3D camera views'}">${['front','left','back','right'].map(name=>`<button type="button" data-hg-view="${name}" aria-pressed="${name==='front'}" disabled>${c[name]}</button>`).join('')}<button type="button" data-hg-orbit aria-pressed="false" disabled>${c.orbit}</button><button type="button" data-hg-fit disabled>${c.fit}</button></div><p class="hg-status" data-hg-status role="status" aria-live="polite">${c.status}</p><p class="hg-help" data-hg-help>${help}</p></div>
  <p class="hg-notice" data-hg-notice>${notice}</p>`;
}
