# -*- mode: python -*-

block_cipher = None

ADD_BINARY = [
        ( 'sqlite3.exe', '.' )
]

ADD_DATA = [
        ( 'templates', 'templates' ),        
        ( 'templates\\admin', 'templates\\admin' ),
        ( 'templates\\admin\\file', 'templates\\admin\\file' ),
        ( 'templates\\admin\\model', 'templates\\admin\\model' ),
        ( 'templates\\admin\\rediscli', 'templates\\admin\\rediscli' ),

        ( 'static', 'static' ),    
        ( 'static\\bootstrap-3.3.7\\css', 'static\\bootstrap-3.3.7\\css' ),    
        ( 'static\\bootstrap-3.3.7\\fonts', 'static\\bootstrap-3.3.7\\fonts' ),    
        ( 'static\\bootstrap-3.3.7\\js', 'static\\bootstrap-3.3.7\\js' ),    

        ( 'static\\datatables-1.10.16\\css', 'static\\datatables-1.10.16\\css' ),    
        ( 'static\\datatables-1.10.16\\images', 'static\\datatables-1.10.16\\images' ),    
        ( 'static\\datatables-1.10.16\\js', 'static\\datatables-1.10.16\\js' ),    

        ( 'static\\admin\\\css\\bootstrap2', 'static\\admin\\\css\\bootstrap2'),
        ( 'static\\admin\\\css\\bootstrap3', 'static\\admin\\\css\\bootstrap3'),
        ( 'static\\admin\\js', 'static\\admin\\js'),

        ( 'static\\bootstrap\\bootstrap2\\css', 'static\\bootstrap\\bootstrap2\\css'),
        ( 'static\\bootstrap\\bootstrap2\\js', 'static\\bootstrap\\bootstrap2\\js'),
        ( 'static\\bootstrap\\bootstrap2\\swatch\\default', 'static\\bootstrap\\bootstrap2\\swatch\\default'),
        ( 'static\\bootstrap\\bootstrap2\\swatch\\img', 'static\\bootstrap\\bootstrap2\\swatch\\img'),

        ( 'static\\bootstrap\\bootstrap3\\css', 'static\\bootstrap\\bootstrap3\\css'),
        ( 'static\\bootstrap\\bootstrap3\\fonts', 'static\\bootstrap\\bootstrap3\\fonts'),
        ( 'static\\bootstrap\\bootstrap3\\js', 'static\\bootstrap\\bootstrap3\\js'),
        ( 'static\\bootstrap\\bootstrap3\\swatch\\default', 'static\\bootstrap\\bootstrap3\\swatch\\default'),
        ( 'static\\bootstrap\\bootstrap3\\swatch\\fonts', 'static\\bootstrap\\bootstrap3\\swatch\\fonts'),

        ( 'static\\vendor', 'static\\vendor'),
        ( 'static\\vendor\\bootstrap-daterangepicker', 'static\\vendor\\bootstrap-daterangepicker'),
        ( 'static\\vendor\\leaflet', 'static\\vendor\\leaflet'),
        ( 'static\\vendor\\leaflet\\images', 'static\\vendor\\leaflet\\images'),
        ( 'static\\vendor\\select2', 'static\\vendor\\select2'),
        ( 'static\\vendor\\x-editable\\css', 'static\\vendor\\x-editable\\css'),
        ( 'static\\vendor\\x-editable\\img', 'static\\vendor\\x-editable\\img'),
        ( 'static\\vendor\\x-editable\\js', 'static\\vendor\\x-editable\\js')
]

a = Analysis(['spoolkit.py'],
             pathex=['C:\\data\\bitbucket\\spoolkit'],
             binaries=ADD_BINARY,
             datas=ADD_DATA,
             hiddenimports=['flask=admin'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='spoolkit',
          debug=False,
          strip=False,
          icon='C:\\data\\bitbucket\\spoolkit\\s.ico',
          upx=True,
          runtime_tmpdir=None,
          console=True )
