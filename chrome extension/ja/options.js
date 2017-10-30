$( document ).ready(function() {
	// $("server_IP").val(localStorage["server_IP"] ? localStorage["server_IP"] : "");
	chrome.storage.sync.get({
	    server_URL: '',
	  }, function(items) {
	    $("#server_URL").val(items.server_URL);
	  });
});
$("#save").click(function(){
	// localStorage["server_IP"] = $("server_IP").val();
	chrome.storage.sync.set({
	    server_URL: $("#server_URL").val(),
	  }, function() {
	    // Update status to let user know options were saved.
	    var status = document.getElementById('status');
	    status.textContent = 'Options saved.';
	    setTimeout(function() {
	      status.textContent = '';
	    }, 750);
	  });
});