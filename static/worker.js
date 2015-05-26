function timedCount() {
    postMessage("GetNewStats");
    setTimeout("timedCount()",3000);
}

timedCount();