<?

$json = file_get_contents('http://api.bootswatch.com/3/');
$swatches = json_decode($json, true);
$swatches['themes'][] = array(
	'less' => 'real_estate'
);
foreach($swatches['themes'] as $swatch) {
	
	$folder_name = str_replace("http://bootswatch.com/", "", $swatch['less']);
	$folder_name = str_replace("/bootswatch.less", "", $folder_name);

	$bootstrap_file = file_get_contents('../bootstrap.less');
	$bootstrap_file = str_replace('<theme>', $folder_name, $bootstrap_file);

	file_put_contents('../'.$folder_name.'.less', $bootstrap_file);

}

die();
foreach($swatches['themes'] as $swatch) {
	
	$folder_name = str_replace("http://bootswatch.com/", "", $swatch['less']);
	$folder_name = str_replace("/bootswatch.less", "", $folder_name);

	if(!is_dir($folder_name))
		mkdir($folder_name);
	
	echo $folder_name."\n";
	$bootswatch_file = basename($swatch['less']);
	$variables_file = basename($swatch['lessVariables']);

	downloadFile($swatch['less'], $folder_name.'/'.$bootswatch_file);
	downloadFile($swatch['lessVariables'], $folder_name.'/'.$variables_file);
}

function downloadFile ($url, $path) {

  $newfname = $path;
  $file = fopen ($url, "rb");
  if ($file) {
    $newf = fopen ($newfname, "wb");

    if ($newf)
    while(!feof($file)) {
      fwrite($newf, fread($file, 1024 * 8 ), 1024 * 8 );
    }
  }

  if ($file) {
    fclose($file);
  }

  if ($newf) {
    fclose($newf);
  }
 }

?>