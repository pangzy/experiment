#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""------------------------------------
test script

arguments:

arg[1]:

-diff : difference test
		same parameter run 10 times each,compare the results
		text output
		(diff_xxx.dat)

-omega_miss  : 	false=0
				omega change as different curve 
				miss change as x-asis
				time saved of hit req as y-asis
				text and chart output
				(om_xxx.dat,om_xxx.pic)

-miss_omega  : 	false=0
			   	miss change as different curve
			   	omega change as x-asis
			   	time saved of hit req as y-asis
			   	text and chart output
			   	(mo_xxx.dat,mo_xxx.pic)

-omega_false : 	miss=0
				omega change as different curve
				false change as x-asis
				time saved hit req as y-asis
				text and chart output
				(of_xxx.dat,of_xxx.pic)

-false_omega : 	miss=0
				false change as different curve
				omega change as x-asis
				time saved of hit req as y-asis
			   	text and chart output
			   	(fo_xxx.dat,fo_xxx.pic)

-omega_miss_false:  miss and false change as different curve
					omega change as x-asis
					time saved of hit req as y-asis
					text and chart output
					(omf_xxx.dat,omf_xxx.pic)

-
------------------------------------"""