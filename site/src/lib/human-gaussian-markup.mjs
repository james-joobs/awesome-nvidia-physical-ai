const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const humanGaussianCopy = {
  en: {
    title:'Compare RGB video with an animated Gaussian model',
    intro:'Inspect a matching RGB video and 3D representation on one timeline. The public rig control and locally trained reconstruction models are labeled by their data source and representation.',
    load:'Load the 3D example',folder:'Open a local result folder',privacy:'Selected files are read in this browser. They are not uploaded.',
    observed:'Source RGB',observedBadge:'OBSERVED',reconstructed:'4D Gaussian reconstruction',inferredBadge:'INFERRED',
    emptySource:'The matching RGB video will appear here.',empty3d:'Load an example or select a result folder to begin.',
    status:'The model is downloaded only when you choose to load it.',play:'Play',pause:'Pause',seek:'Playback position',
    front:'Front',left:'Left',back:'Back',right:'Right',orbit:'Auto orbit',fit:'Fit view',close:'Close 3D',
    compare:'Compare',source:'RGB only',model:'3D only',help:'Drag: orbit · Scroll/pinch: zoom · Right drag: pan. The same timeline controls both panels.',
    sourceCredit:'Source and license',reference:'YouTube reference',referenceTitle:'Original reference video',
    referenceText:'This external reference is separate from the synthetic SOMA control below. It is not the RGB source of the public sample. Watch the original in the official YouTube player.',
    referenceLink:'Watch the original on YouTube',referenceChannel:'지숭이_Jisoong · 체포하겠어🚨🚨',
    notice:'Unobserved surfaces are generated estimates. Camera calibration, fine detail and temporal consistency can remain imperfect.',
    manifest:'Result manifest',time:'0.00 / — s',download:'Download and GPU memory use depend on the selected segment.',
  },
  ko: {
    title:'RGB 영상과 Gaussian 동작 표현 비교하기',
    intro:'대응하는 RGB 영상과 3D 표현을 한 타임라인으로 살펴봅니다. 공개 리깅 제어 샘플과 직접 학습한 로컬 재구성 모델은 출처와 표현 방식을 구분해 표시합니다.',
    load:'3D 예제 불러오기',folder:'로컬 결과 폴더 열기',privacy:'선택한 파일은 이 브라우저에서만 읽으며 업로드하지 않습니다.',
    observed:'원본 RGB',observedBadge:'실제 관측',reconstructed:'인체 4D Gaussian 재구성',inferredBadge:'추정 외형 포함',
    emptySource:'대응하는 원본 RGB 영상이 여기에 표시됩니다.',empty3d:'예제를 불러오거나 결과 폴더를 선택하세요.',
    status:'불러오기 전에는 모델을 내려받지 않습니다.',play:'재생',pause:'일시 정지',seek:'재생 위치',
    front:'정면',left:'왼쪽',back:'뒤',right:'오른쪽',orbit:'자동 회전',fit:'화면에 맞추기',close:'3D 닫기',
    compare:'함께 보기',source:'RGB 크게 보기',model:'3D 크게 보기',help:'드래그: 회전 · 휠/두 손가락: 확대 · 오른쪽 드래그: 이동. 아래 타임라인이 두 화면을 함께 제어합니다.',
    sourceCredit:'원본 출처와 라이선스',reference:'YouTube 참고 자료',referenceTitle:'원본 참고 영상',
    referenceText:'이 외부 참고 영상은 아래 SOMA 합성 제어 샘플과 별개의 자료이며, 공개 샘플의 RGB 원본이 아닙니다. 원본은 공식 YouTube 플레이어로 확인할 수 있습니다.',
    referenceLink:'YouTube에서 원본 보기',referenceChannel:'지숭이_Jisoong · 체포하겠어🚨🚨',
    notice:'관측하지 않은 표면은 생성 모델이 추정합니다. 카메라 정합, 얼굴·손의 세부 형태, 시간에 따른 일관성에는 한계가 남을 수 있습니다.',
    manifest:'실행 정보',time:'0.00 / — s',download:'선택한 구간에 따라 내려받는 용량과 GPU 메모리 사용량이 달라집니다.',
  },
};
export function humanGaussianMarkup(locale='en',{manifestUrl='',reference=true,controlSample=false,youtubeSource=false,sourcePosterUrl='',modelPosterUrl=''}={}) {
  const ko=locale==='ko',c=humanGaussianCopy[ko?'ko':'en'];
  const sourceTitle=controlSample?(ko?'SOMA 합성 RGB · 제어 샘플':'SOMA synthetic RGB · control'):c.observed,sourceBadge=controlSample?(ko?'합성 렌더':'SYNTHETIC RENDER'):c.observedBadge,modelTitle=controlSample?(ko?'SOMA 리깅 Gaussian 제어 샘플':'SOMA rigged Gaussian control'):c.reconstructed,modelBadge=controlSample?(ko?'알려진 리깅':'KNOWN RIG'):c.inferredBadge;
  const intro=youtubeSource?(ko?'원본은 왼쪽 YouTube 공식 플레이어로, 복원한 4D Gaussian은 오른쪽에서 둘러봅니다. 원본과 3D의 재생 위치는 각각 조절합니다.':'Watch the original in the official YouTube player and orbit the reconstructed 4D Gaussian on the right. The two players have independent playback controls.'):c.intro;
  const help=youtubeSource?(ko?'드래그: 회전 · 휠: 확대. 아래 타임라인은 3D를 제어합니다. 원본은 YouTube 플레이어에서 재생하세요.':'Drag: orbit · Scroll: zoom. This timeline controls 3D only; use the official YouTube player for the original.'):c.help;
  const notice=controlSample?(ko?'이 공개 샘플은 SOMA의 공식 중립 체형과 예제 동작을 Gaussian으로 그린 리깅 제어 예제입니다. RGB 영상에서 외형을 학습한 결과나 위 YouTube 인물의 모델이 아닙니다.':'This public control renders SOMA’s official neutral body and example motion as rigged Gaussians. It is not an RGB-trained reconstruction or a model of the person in the YouTube reference.'):c.notice;
  return `${reference&&!youtubeSource?`<section class="hg-reference" aria-label="${c.reference}"><div><span class="hg-kicker">${c.reference}</span><h3>${c.referenceTitle}</h3><p>${c.referenceText}</p><p><a href="https://www.youtube.com/shorts/rWS8uli1-m0" target="_blank" rel="noopener noreferrer">${c.referenceChannel}</a></p></div><iframe src="https://www.youtube-nocookie.com/embed/rWS8uli1-m0?playsinline=1&amp;rel=0" title="${c.referenceChannel}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></section>`:''}
  <header class="hg-heading"><h2>${c.title}</h2><p>${intro}</p></header>
  <div class="hg-load-row"><button type="button" data-hg-load ${manifestUrl?'':'hidden'}>${c.load}</button><label class="hg-folder"><input type="file" data-hg-folder webkitdirectory multiple><span>${c.folder}</span></label><p>${c.privacy}</p></div>
  <div class="hg-display-modes" role="group" aria-label="${locale==='ko'?'비교 화면 구성':'Comparison layout'}"><button type="button" data-hg-mode="compare" aria-pressed="true">${c.compare}</button><button type="button" data-hg-mode="source" aria-pressed="false">${c.source}</button><button type="button" data-hg-mode="model" aria-pressed="false">${c.model}</button></div>
  <div class="hg-pair" data-hg-pair data-mode="compare"><section class="hg-panel hg-source-panel"><div class="hg-panel-head"><h3 data-hg-source-title>${sourceTitle}</h3><span data-hg-source-badge>${sourceBadge}</span></div><div class="hg-source-stage"><video data-hg-source ${youtubeSource?'hidden':''} muted playsinline preload="metadata" ${sourcePosterUrl?`poster="${escape(sourcePosterUrl)}"`:""} aria-label="${c.observed}"></video>${youtubeSource?`<iframe data-hg-youtube src="https://www.youtube-nocookie.com/embed/rWS8uli1-m0?playsinline=1&amp;rel=0" title="${c.referenceChannel}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>`:""}<p class="hg-empty" data-hg-source-empty ${sourcePosterUrl||youtubeSource?"hidden":""}>${c.emptySource}</p></div><p class="hg-credit" data-hg-credit>${youtubeSource?'<a href="https://www.youtube.com/shorts/rWS8uli1-m0" target="_blank" rel="noopener noreferrer">지숭이_Jisoong · 체포하겠어🚨🚨 · YouTube</a>':controlSample?'<a href="https://github.com/NVlabs/SOMA-X">NVIDIA SOMA-X</a> · Apache-2.0 · synthetic control':''}</p></section>
  <section class="hg-panel hg-model-panel"><div class="hg-panel-head"><h3 data-hg-model-title>${modelTitle}</h3><span data-hg-model-badge>${modelBadge}</span></div><div class="hg-stage" data-hg-stage>${modelPosterUrl?`<img class="hg-poster" data-hg-poster src="${escape(modelPosterUrl)}" alt="${escape(modelTitle)}" loading="lazy">`:""}<p class="hg-empty ${modelPosterUrl?"hg-overlay":""}" data-hg-cover>${c.empty3d}</p><output class="hg-view-label" data-hg-view-label>${c.front}</output></div><p class="hg-model-info" data-hg-info>${c.download}</p></section></div>
  <div class="hg-controls"><div class="hg-timeline"><button type="button" data-hg-play disabled>${c.play}</button><output data-hg-time>${c.time}</output><input type="range" data-hg-seek min="0" max="120" step="1" value="0" aria-label="${c.seek}" disabled><button type="button" data-hg-close disabled>${c.close}</button></div><div class="hg-views" role="group" aria-label="${locale==='ko'?'3D 카메라 시점':'3D camera views'}">${['front','left','back','right'].map(name=>`<button type="button" data-hg-view="${name}" aria-pressed="${name==='front'}" disabled>${c[name]}</button>`).join('')}<button type="button" data-hg-orbit aria-pressed="false" disabled>${c.orbit}</button><button type="button" data-hg-fit disabled>${c.fit}</button></div><p class="hg-status" data-hg-status role="status" aria-live="polite">${c.status}</p><p class="hg-help" data-hg-help>${help}</p></div>
  <p class="hg-notice" data-hg-notice>${notice}</p><p class="hg-provenance" data-hg-provenance></p><a data-hg-manifest hidden>${c.manifest}</a>`;
}
