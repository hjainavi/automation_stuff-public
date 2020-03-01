set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.


Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
Plugin 'tpope/vim-fugitive'
Plugin 'tpope/vim-obsession'
" Plugin 'davidhalter/jedi-vim'
" Plugin 'nvie/vim-flake8'
" Plugin 'Yggdroot/indentLine'

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line

set tabstop=4
set softtabstop=4
set shiftwidth=4
set textwidth=0
set expandtab
set autoindent
set fileformat=unix
set pastetoggle=<F2>
hi MatchParen cterm=none ctermbg=green ctermfg=blue

set encoding=utf-8
let g:airline_theme='dark'
let g:airline_section_c = '%F'
set nu 
set t_Co=256
set noshowmode
let g:airline_section_a = airline#section#create_left([])
let g:airline_section_z = airline#section#create(['linenr', 'maxlinenr', ':%3v  '])
let g:airline_section_warning = airline#section#create(['whitespace'])
let g:airline_section_y = airline#section#create_right([])
let g:airline_section_x = airline#section#create_right([])

set hlsearch
hi Search guifg=LightBlue ctermfg=LightBlue
syntax on
set clipboard=unnamed

