function startAiTraining() {
    const modal = document.getElementById('ai-training-modal');
    modal.classList.remove('hidden');
    document.getElementById('ai-train-name-1').innerText = "Loading...";
    
    fetch('/api/faces/training_pairs')
        .then(res => res.json())
        .then(data => {
            trainingPairs = data.pairs || [];
            currentPairIndex = 0;
            showNextTrainingPair();
        });
}

function showNextTrainingPair() {
    if (currentPairIndex >= trainingPairs.length) {
        document.getElementById('ai-training-modal').classList.add('hidden');
        alert("No more faces to train right now. Great job!");
        renderPeopleList();
        return;
    }
    
    const pair = trainingPairs[currentPairIndex];
    document.getElementById('ai-train-name-1').innerText = pair.person_name;
    document.getElementById('ai-train-img-1').src = `/api/photo/crop/${pair.named_face_id}`;
    document.getElementById('ai-train-img-2').src = `/api/photo/crop/${pair.unknown_face_id}`;
}