var reverse_dns = reverse_dns || {};

reverse_dns.utils = reverse_dns.utils || {};

reverse_dns.helpers = {};

reverse_dns.data = {
	'ip_address' : 'IP Address'
};

/**
	Utility function to perform all Ajax GET and POST calls
*/
reverse_dns.utils.do_ajax = function (type, url, data, success, error) {
    return $.ajax({
            url: url,
            dataType: "json",
	        type: type,
	        data: data,
	        contentType: "application/json; charset=utf-8",
	        headers: {
	               "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val(),
	        },
	        success: success,
	        error: error
	    });
}


$(function(){
	var lbl = "Add IP";
	var img = "<img src=\"/static/images/spinner.gif\" alt=\"Wait\" />";

	$("#add_domains").button();

	$("input").on('focus',function(){
		if ($(this).val() == reverse_dns.data[$(this).attr('name')]) { $(this).val('');}
	});

	$("#add_domains").on('click',function(){
		$("#add_domains").html(img+"&nbsp;&nbsp;"+lbl);

		reverse_dns.utils.do_ajax('post',
				'/reversedns/lookup/add_domains/',
				{'ip_address' : $("#ip_address").val()},
				function(data){reverse_dns.helpers.add_domains(data);},
				function(data) {reverse_dns.helpers.error()});

	});
});

/**
	Helper method for the Add IP Address functionality.  
	Called when Adding an IP succeeds.
*/
reverse_dns.helpers.add_domains = function(data) {

	data = eval(data);
	if (data[0].status == 200) {
		alert('we are ready to proceed');
	}
};

/**
	Helper method for All Aajax failures
*/
reverse_dns.helpers.error = function() {
	alert('error');
};
