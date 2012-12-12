var reverse_dns = reverse_dns || {};
reverse_dns.utils = reverse_dns.utils || {};

reverse_dns.utils.datatable_factory = function(server_side, url, aoColumns, $table, aaData, success) {

	var datatable = {
		"bDestroy"        : true,
		"bJQueryUI"       : false,
		"bPaginate"       : true,
        "bLengthChange"   : false,
        "iDisplayLength"  : 10,
        "bFilter"         : false,
        "bSort"           : false,
        "bInfo"           : true,
        "bAutoWidth"      : true,
        "bProcessing"     : true,
       	"sPaginationType" : "full_numbers",
       	"aoColumns"       : aoColumns
       	
	}

	if (server_side) {
		datatable["bServerSide"]  = server_side,
		datatable["sAjaxSource"]  = url,
		datatable["fnServerData"] = function(sSource, aoData, fnCallback) {
			reverse_dns.utils.do_ajax('post', sSource, aoData, function(data){success(fnCallback, data)});
		}	
	} else {
		datatable["aaData"]     = aaData
	}

	$table.dataTable(datatable);

}