# cell_cropper_gui

複数の細胞を含む画像から、細胞部分のみを指定したピクセルサイズで連続して切り出し、npyファイル形式で保存します。保存したnpyファイルはそのままtensorflowなどのディープラーニングフレームワークでの解析に用いることが可能です。

ubuntu 14.04
anaconda 3-4.2.0 (python 3.5.2)
opencv 3.1.0

にて動作確認済。

`python Cell_Cropper.py`を実行するだけでGUIが立ち上がります。または、サイドバーから起動する場合には、
    
    cd ~/.local/share/applications/
    nano cellcropper.desktop

を行い、cellcropper.desktopに下記を書き込んで保存してください。
    
    [Desktop Entry]
    Type=Application
    Name=Cell Cropper
    Comment=Cell Cropper
    Icon=[icon pass]
    Exec=[python pass] [Cell_Cropper.pyのpass]
    Terminal=false
    
そののちに下記を実行してアイコンをサイドバーにドラッグすればサイドバーから起動できるようになります。

    chmod a+x ~/.local/share/applications/cellcropper.desktop 
    nautilus ~/.local/share/applications

具体的な使用例の動画はこちらです。https://www.youtube.com/watch?v=VCa57YnaCGI
