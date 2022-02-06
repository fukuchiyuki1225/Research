RM = rm -f
PLATEX = platex
DVI2PDF = dvipdfmx

########################################################################

all:	thesis_sample.pdf master_sample.pdf

thesis_sample.pdf:	thesis_sample.tex wuse_thesis.sty
	${MAKE} thesis-clean
	${PLATEX} thesis_sample.tex
	${PLATEX} thesis_sample.tex
	${PLATEX} thesis_sample.tex
	${DVI2PDF} thesis_sample.dvi

master_sample.pdf:	master_sample.tex wuse_thesis.sty
	${MAKE} master-clean
	${PLATEX} master_sample.tex
	${DVI2PDF} master_sample.dvi

resume_sample.pdf:	resume_sample.tex wuse_resume.sty
	${MAKE} resume-clean
	${PLATEX} resume_sample.tex
	${PLATEX} resume_sample.tex
	${PLATEX} resume_sample.tex
	${DVI2PDF} resume_sample.dvi

########################################################################

clean::
	${MAKE} thesis-clean
	${MAKE} master-clean
	${MAKE} resume-clean

thesis-clean::
	${RM} thesis_sample.aux
	${RM} thesis_sample.dvi
	${RM} thesis_sample.log
	${RM} thesis_sample.toc

master-clean::
	${RM} master_sample.aux
	${RM} master_sample.dvi
	${RM} master_sample.log

resume-clean::
	${RM} resume_sample.aux
	${RM} resume_sample.dvi
	${RM} resume_sample.log
