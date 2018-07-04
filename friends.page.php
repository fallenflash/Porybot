<?php 
$user = $_GET['user'];
$code = $_GET['code'];
?>
<div class="row align-items-center">
	<h3> Friend Code Sharing </h3>
</div>
<div class="row align-items-center">
	<div class="col">
		<h2>
			<?php echo $user; ?>
		</h2>
		<table class="table">
			<thead>
				<tr>
					<th scope="col">Friend Code</th>
					<th scope="col"> </th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>
						<?= $code ?>
					</td>
					<td>
						<button id="friendbutton" class="btn btn-info" data-clipboard-text="<?php echo $code; ?>">Click to Copy</button>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</div>
<div id="snackbar"><?php echo $user; ?>'s code was copied succesfully</div>
<script src="https://cdn.jsdelivr.net/npm/clipboard@2/dist/clipboard.min.js"></script>
<script>
    var btn = document.getElementById('friendbutton');
	var clipboard = new ClipboardJS(btn);
    var x = document.getElementById("snackbar");

    clipboard.on('success', function (e) {
        x.className = "show";
        setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
    	console.log(e);
    });
    clipboard.on('error', function (e) {
    	console.log(e);
    });

</script>
<style>
 #snackbar {
    visibility: hidden;
    min-width: 250px; 
    margin-left: -125px; 
    background-color: #333; 
    color: #fff; 
    text-align: center; 
    border-radius: 2px; 
    padding: 16px; 
    position: fixed; 
    z-index: 1; 
    left: 50%; 
    bottom: 30px; 
}


#snackbar.show {
    visibility: visible; 


    -webkit-animation: fadein 0.5s, fadeout 0.5s 2.5s;
    animation: fadein 0.5s, fadeout 0.5s 2.5s;
}


@-webkit-keyframes fadein {
    from {bottom: 0; opacity: 0;}
    to {bottom: 30px; opacity: 1;}
}

@keyframes fadein {
    from {bottom: 0; opacity: 0;}
    to {bottom: 30px; opacity: 1;}
}

@-webkit-keyframes fadeout {
    from {bottom: 30px; opacity: 1;}
    to {bottom: 0; opacity: 0;}
}

@keyframes fadeout {
    from {bottom: 30px; opacity: 1;}
    to {bottom: 0; opacity: 0;}
} 
</style>
