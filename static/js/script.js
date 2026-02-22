function handleResponse(data) {
    const imgEl = document.getElementById('scannedImage');
    const videoEl = document.getElementById('webcam');
    const laserEl = document.getElementById('laser');

    if(data.annotated_image) {
        imgEl.src = data.annotated_image;
        imgEl.classList.remove('d-none');
        // Stop camera logic
        if (streamPtr) streamPtr.getTracks().forEach(t => t.stop());
        videoEl.srcObject = null;
        document.getElementById('startBtn').classList.remove('d-none');
        document.getElementById('stopBtn').classList.add('d-none');
        laserEl.style.display = 'none';
    }
    updateUI(data);
}

function updateUI(data) {
    const billBody = document.getElementById('billBody');
    if (data.bill && data.bill.length > 0) {
        billBody.innerHTML = data.bill.map(item => `
            <div class="item-row d-flex justify-content-between align-items-center p-2 border-bottom">
                <span><strong class="text-dark">${item.name}</strong> <small class="text-muted">x${item.qty}</small></span>
                <span class="fw-bold text-success">${item.sub}</span>
            </div>`).join('');
        
        currentTotal = data.total;
        document.getElementById('totalDisplay').innerText = data.total;
        document.getElementById('payBtn').disabled = false;
        document.getElementById('clearBtn').disabled = false;
    } else {
        billBody.innerHTML = '<div class="text-center py-5 opacity-50"><p>No items recognized. Try again.</p></div>';
    }
}