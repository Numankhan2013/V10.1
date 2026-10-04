  /* NK_ICON_REFINEMENT_V1_START */
  // Enrich existing, familiar geometry. These are offline vector glyphs, not
  // new controls or behavioral wrappers; labels and action ownership stay put.
  function nkIconLayers(markup,layers,name){
    return markup.replace('<svg ',`<svg class="nk-product-icon" data-nk-icon="${name}" focusable="false" `)
      .replace(/stroke-width="[\d.]+"/,'stroke-width="2"')
      .replace(/(<svg\b[^>]*>)/,`$1<g class="nk-icon-tone" fill="currentColor" stroke="none" opacity=".18">${layers}</g>`);
  }
  const nkIconBase=navIcon;
  const nkIconPlanes={
    home:'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1V10Z"/><path opacity=".55" d="m12 3 9 7v10a1 1 0 0 1-1 1h-5v-7h-3V3Z"/>',
    book:'<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21V5.5Z"/><path opacity=".7" d="M6.5 3H9v16H6.5A2.5 2.5 0 0 0 4 21V5.5A2.5 2.5 0 0 1 6.5 3Z"/>',
    test:'<rect x="6" y="3" width="12" height="18" rx="2"/><path opacity=".7" d="M14 3h2a2 2 0 0 1 2 2v3h-4V3Z"/>',
    chart:'<path d="M7 19v-4l3-4 3 2 5-7v13H7Z"/><path opacity=".5" d="m13 13 5-7v13h-5v-6Z"/>',
    bookmark:'<path d="M6 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18l-6-3-6 3V4Z"/><path opacity=".55" d="M12 2h4a2 2 0 0 1 2 2v18l-6-3V2Z"/>',
    clock:'<circle cx="12" cy="12" r="8.5"/><path opacity=".7" d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5H12V3.5Z"/>',
    search:'<circle cx="11" cy="11" r="6.5"/><path opacity=".6" d="M11 4.5a6.5 6.5 0 0 1 6.5 6.5H11V4.5Z"/>',
    bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9Z"/>',
    star:'<path d="m12 3 2.9 5.9 6.1.9-4.4 4.3 1 6.1L12 18.3 6.4 21.2l1-6.1L3 9.8l6.1-.9L12 3Z"/>',
    trash:'<path d="m7 7 1 13h8l1-13H7Z"/><path opacity=".65" d="M9 4h6v3H9V4Z"/>',
    refresh:'<circle cx="12" cy="12" r="6"/><path opacity=".6" d="M12 6a6 6 0 0 1 6 6h-6V6Z"/>',
    share:'<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/>',
    molecule:'<circle cx="6" cy="12" r="2.5"/><circle cx="17.5" cy="6" r="2.5"/><circle cx="17.5" cy="18" r="2.5"/>',
    bulb:'<path d="M8.5 15.5A7 7 0 1 1 15.5 15.5L14 18h-4l-1.5-2.5Z"/>',
    heart:'<path d="M12 21s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.6-7 10-7 10Z"/>',
    body:'<circle cx="12" cy="5" r="2.2"/>',
    dna:'<path d="M5 3h14c-7 0-7 18-14 18h14C12 21 12 3 5 3Z"/>'
  };
  navIcon=function(name,size=21){
    let markup=nkIconBase(name,size);
    if(name==='grid'){
      const tiles='<rect x="4" y="4" width="6" height="6" rx="1.6"/><rect x="14" y="4" width="6" height="6" rx="1.6"/><rect x="4" y="14" width="6" height="6" rx="1.6"/><rect x="14" y="14" width="6" height="6" rx="1.6"/>';
      markup=markup.replace(/>.*<\/svg>$/,`>${tiles}</svg>`);
      return nkIconLayers(markup,tiles,name);
    }
    if(name==='more')return nkIconLayers(markup,'',name).replace('fill="none"','fill="currentColor"').replaceAll('r="1"','r="1.4"');
    if(['back','chevron','check','close','pause','menu'].includes(name))return nkIconLayers(markup,'',name).replace('stroke-width="2"','stroke-width="2.2"');
    return nkIconLayers(markup,nkIconPlanes[name]||'',name);
  };
  const nkSubjectIconBase=nkSubjectGraphic;
  nkSubjectGraphic=function(name,size=20){
    const key=nkAppSubjectMeta(name).key;
    const plane={
      biochemistry:'<path d="M7 4h10c0 3-2 5-5 8s-5 5-5 8h10c0-3-2-5-5-8S7 7 7 4Z"/>',
      physiology:'<path d="m12 21-7.5-7.43A5 5 0 0 1 12 7a5 5 0 1 1 7.5 6.57L12 21Z"/>',
      anatomy:'<path d="M15 3a3 3 0 0 1 3 3a3 3 0 1 1-2.12 5.122l-4.758 4.758a3 3 0 1 1-5.117 2.297v-.177h-.176a3 3 0 1 1 2.298-5.115l4.758-4.758A3 3 0 0 1 15 3Z"/>',
      poisoning:'<path d="m7.5 14-2.5 4a2 2 0 0 0 1.75 3h10.5A2 2 0 0 0 19 18l-2.5-4h-9Z"/>',
      ophthalmology:'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/>',
      'male-reproductive':'<circle cx="9" cy="15" r="6"/>',
      'female-reproductive':'<circle cx="12" cy="8" r="5"/>',
      pregnancy:'<circle cx="10" cy="4" r="2"/><path d="M9 8h3l1 3c4 0 6 2 6 5H9V8Z"/>',
      uworld:nkIconPlanes.book
    };
    return nkIconLayers(nkSubjectIconBase(name,size),plane[key]||'',key).replace('class="nk-product-icon"','class="nk-product-icon nk-subject-svg"').replace(' class="nk-subject-svg"','');
  };
  const nkAnalysisIconBase=nkAnalysisIcon;
  nkAnalysisIcon=function(name,size=18){
    const markup=nkAnalysisIconBase(name,size);
    const plane=name==='edit'?'<path d="m15 4 5 5-11 11H4v-5L15 4Z"/>':name==='minus'?'':'<circle cx="12" cy="13" r="8"/>';
    return nkIconLayers(markup,plane,name==='minus'?'minus':name==='edit'?'edit':'stopwatch');
  };
  /* NK_ICON_REFINEMENT_V1_END */
