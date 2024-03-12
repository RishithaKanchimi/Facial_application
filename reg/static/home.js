window.onload = function() {
	document.getElementById("searchTextBox").focus();
};

function enableCapturePhotoBlock() {
	document.getElementById("photoCaptureBlock").style.visibility = "visible";
}

function runScript(e) {
    if (e.keyCode == 13) {
        var rollNo = document.getElementById("searchTextBox").value;
        $.ajax({
    	    url: 'getCandidatePhotoDetails?roll_no=' + rollNo,
    	    type: 'GET',
    	    success: function(data){
    	    	if (data != "") {
    	    		document.getElementById("photoCaptureBlock").style.visibility = "visible";
    	    		if (data.registrationPhoto != null) {
    	    			document.getElementById("photo1").src = "data:image/jpeg;base64," + data.registrationPhoto;	
    	    		} else {
    	    			document.getElementById("photo1").src = "images/img_not_found.png";
    	    		}
    	    		
    	    		if (data.prelimsPhoto != null) {
    	    			document.getElementById("photo2").src = "data:image/jpeg;base64," + data.prelimsPhoto;	
    	    		} else {
    	    			document.getElementById("photo2").src = "images/img_not_found.png";
    	    		}
    	    		
    	    		if (data.mainsMorningPhoto != null) {
    	    			document.getElementById("photo3").src = "data:image/jpeg;base64," + data.mainsMorningPhoto;
    	    		} else {
    	    			document.getElementById("photo3").src = "images/img_not_found.png";
    	    		}
    	    		
    	    		if (data.mainsEveningPhoto != null) {
    	    			document.getElementById("photo4").src = "data:image/jpeg;base64," + data.mainsEveningPhoto;
    	    		} else {
    	    			document.getElementById("photo4").src = "images/img_not_found.png";
    	    		}
    	    	} else {
    	    		displayRedPopup("Candidate details are not avaiable.");
    	    	}
    	    },
    	    error: function(jqXhr){
    	    	displayRedPopup("Please check the service being started or restart it again.");
    	    }
    	});
    }
}

function callPhotoVerification() {
	
	document.getElementById("callPhotoVerificationButton").disabled = true;
	document.getElementById("startbutton").disabled = true;
	
	document.getElementById("loader").style.display = "block";
	document.getElementById("opacity").style.opacity = ".5";
	
	var rollNo = document.getElementById("searchTextBox").value;
	var candidatePhoto = document.getElementById("candidatePhoto").value;          

	$.ajax({
	    url: 'photoVerification',
	    type: 'POST',
	    data: {'candidatePhoto': candidatePhoto,
	    	   'rollNo': rollNo },
	    success: function(data){
	    	if (data != "") {
	    		if(data == "Images Are Matched") {
	    			displayGreenPopup(data);
	    		} else {
	    			displayRedPopup(data);
	    		}
	    		document.getElementById("loader").style.display = "none";
	    		document.getElementById("opacity").style.opacity = "1";
	    	} else {
	    		displayRedPopup("Something wrong with server side, please contact Administrator or relogin again.");
	    	}
	    },
	    error: function(jqXhr){
	    	displayRedPopup("Please check the service being started or restart it again.");
	    }
	});
	
}

function hideBlocks() {
	document.getElementById("searchTextBox").value = "";
	document.getElementById("photoCaptureBlock").style.visibility = "hidden";
	
	document.getElementById("photo1").src = "#";
	document.getElementById("photo2").src = "#";
	document.getElementById("photo3").src = "#";
	document.getElementById("photo4").src = "#";
	document.getElementById("photo").src = "images/white-image.png";
	
	document.getElementById("callPhotoVerificationButton").disabled = false;
	document.getElementById("startbutton").disabled = false;
	
	document.getElementById("searchTextBox").focus();
}

function displayRedPopup(text) {
	document.getElementById("greenText").innerHTML = "";
	document.getElementById("redText").innerHTML = "";
	document.getElementById("redText").innerHTML = text;
	document.getElementById("resultImage").src = "images/incorrect.png"
	 $('#myModal').modal({
	        show:true,
	        keyboard: false,
	        backdrop: 'static'
	  });
}

function displayGreenPopup(text) {
	document.getElementById("greenText").innerHTML = "";
	document.getElementById("redText").innerHTML = "";
	document.getElementById("greenText").innerHTML = text;
	document.getElementById("resultImage").src = "images/correct.png"
	 $('#myModal').modal({
	        show:true,
	        keyboard: false,
	        backdrop: 'static'
	  });
}

