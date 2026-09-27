import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# 1. Update playSkiper79Transition signature and logic
old_79_signature = "function playSkiper79Transition(titleText, callback) {"
new_79_signature = "function playSkiper79Transition(titleText, callback, overridePhotos = null) {"

js_code = js_code.replace(old_79_signature, new_79_signature)

old_79_logic = """    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    let imgsToUse = [];
    if (photos.length > 0) {
        let pool = [...photos].sort(() => 0.5 - Math.random());
        // Pick 4 random photos for the collage
        while(pool.length > 0 && imgsToUse.length < 4) {
            imgsToUse.push(pool.pop());
        }
    }"""

new_79_logic = """    const fallbackPhotos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const photos = (overridePhotos && overridePhotos.length > 0) ? overridePhotos : fallbackPhotos;
        
    let imgsToUse = [];
    if (photos.length > 0) {
        let pool = [...photos].sort(() => 0.5 - Math.random());
        // Pick 4 random photos for the collage
        while(pool.length > 0 && imgsToUse.length < 4) {
            imgsToUse.push(pool.pop());
        }
        // If we have fewer than 4 (e.g. only 2 top person photos), duplicate them to fill the collage
        let idx = 0;
        while(imgsToUse.length < 4 && imgsToUse.length > 0) {
            imgsToUse.push(photos[idx % photos.length]);
            idx++;
        }
    }"""

js_code = js_code.replace(old_79_logic, new_79_logic)

# 2. Update nextRecapSlide
old_next = """function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        let nextSlideId = recapSlides[recapCurrentSlide + 1].id;
        
        let transitionTitle = null;
        if (nextSlideId === 'slide-person') transitionTitle = "TOP PERSON";
        if (nextSlideId === 'slide-place') transitionTitle = "ICONIC PLACE";
        if (nextSlideId === 'slide-hero') transitionTitle = "HERO MOMENT";
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });"""

new_next = """function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        let nextSlideId = recapSlides[recapCurrentSlide + 1].id;
        
        let transitionTitle = null;
        let transitionPhotos = null;
        
        if (nextSlideId === 'slide-person') { transitionTitle = "TOP PERSON"; transitionPhotos = recapData?.top_person_photos || null; }
        if (nextSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }
        if (nextSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.memorable_moment ? [recapData.memorable_moment] : null; }
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            }, transitionPhotos);"""

js_code = js_code.replace(old_next, new_next)

# 3. Update prevRecapSlide
old_prev = """function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        let prevSlideId = recapSlides[recapCurrentSlide - 1].id;
        
        let transitionTitle = null;
        if (prevSlideId === 'slide-person') transitionTitle = "TOP PERSON";
        if (prevSlideId === 'slide-place') transitionTitle = "ICONIC PLACE";
        if (prevSlideId === 'slide-hero') transitionTitle = "HERO MOMENT";
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });"""

new_prev = """function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        let prevSlideId = recapSlides[recapCurrentSlide - 1].id;
        
        let transitionTitle = null;
        let transitionPhotos = null;
        
        if (prevSlideId === 'slide-person') { transitionTitle = "TOP PERSON"; transitionPhotos = recapData?.top_person_photos || null; }
        if (prevSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }
        if (prevSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.memorable_moment ? [recapData.memorable_moment] : null; }
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            }, transitionPhotos);"""

js_code = js_code.replace(old_prev, new_prev)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Updated slide transitions to use context-specific images!")
