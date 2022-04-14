PRJ_NAME=$(shell basename "$(PWD)")
PRJ_DESC=<$(PRJ_NAME)>는 캡스톤 프로젝트 백엔드 프로그램입니다.
PRJ_BASE=$(shell pwd)
CONT_NAME=$(PRJ_NAME)
.DEFAULT: help
.SILENT:;

##help : 도움말 (기본 명령)
help: Makefile
	echo ""
	echo " $(PRJ_DESC)"
	echo ""
	echo " 사용 방법 : "
	echo ""
	echo " make 실행 명령"
	echo ""
	sed -n 's/^##/	/p' $< | column -t -s ':' |  sed -e 's/^/ /'
	echo ""

##all : 모든 실행 파일을 빌드하며, 새로운 개발 문서를 작성
all:
	# 빌드 명령
	echo " > Compile Done."

d-build:
	docker container list -al