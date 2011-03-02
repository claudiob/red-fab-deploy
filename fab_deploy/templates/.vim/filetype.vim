if exists("did_load_filetypes")
	finish
endif

augroup filetypedetect
	au! BufNewFile,BufRead *.ck setf ck
	augroup END
