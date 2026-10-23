; benchmark generated from python API
(set-info :status unknown)
(declare-fun liveness_0_0 () Int)
(declare-fun liveness_0_1 () Int)
(declare-fun liveness_0_2 () Int)
(declare-fun liveness_0_3 () Int)
(declare-fun liveness_0_4 () Int)
(assert
 (let (($x79 (= liveness_0_0 3)))
 (let (($x112 (= liveness_0_0 2)))
 (let (($x261 (= liveness_0_0 1)))
 (let (($x406 (= liveness_0_0 0)))
 (or $x406 $x261 $x112 $x79))))))
(assert
 (not (or (= liveness_0_0 2))))
(assert
 (let (($x331 (= liveness_0_1 3)))
 (let (($x399 (= liveness_0_1 2)))
 (let (($x344 (= liveness_0_1 1)))
 (let (($x354 (= liveness_0_1 0)))
 (or $x354 $x344 $x399 $x331))))))
(assert
 (not (or (= liveness_0_1 2))))
(assert
 (let (($x29 (= liveness_0_2 3)))
 (let (($x86 (= liveness_0_2 2)))
 (let (($x77 (= liveness_0_2 1)))
 (let (($x445 (= liveness_0_2 0)))
 (or $x445 $x77 $x86 $x29))))))
(assert
 (not (or (= liveness_0_2 2))))
(assert
 (let (($x33 (= liveness_0_3 3)))
 (let (($x113 (= liveness_0_3 2)))
 (let (($x435 (= liveness_0_3 1)))
 (let (($x501 (= liveness_0_3 0)))
 (or $x501 $x435 $x113 $x33))))))
(assert
 (not (or (= liveness_0_3 2))))
(assert
 (let (($x177 (= liveness_0_4 3)))
 (let (($x395 (= liveness_0_4 2)))
 (let (($x437 (= liveness_0_4 1)))
 (or (= liveness_0_4 0) $x437 $x395 $x177)))))
(assert
 (not (or (= liveness_0_4 2))))
(assert
 (= liveness_0_0 0))
(assert
 (or (and (= liveness_0_0 0) (= liveness_0_1 1)) (and (= liveness_0_0 1) (= liveness_0_1 2)) (and (= liveness_0_0 2) (= liveness_0_1 3)) (and (= liveness_0_0 3) (= liveness_0_1 3))))
(assert
 (or (and (= liveness_0_1 0) (= liveness_0_2 1)) (and (= liveness_0_1 1) (= liveness_0_2 2)) (and (= liveness_0_1 2) (= liveness_0_2 3)) (and (= liveness_0_1 3) (= liveness_0_2 3))))
(assert
 (or (and (= liveness_0_2 0) (= liveness_0_3 1)) (and (= liveness_0_2 1) (= liveness_0_3 2)) (and (= liveness_0_2 2) (= liveness_0_3 3)) (and (= liveness_0_2 3) (= liveness_0_3 3))))
(assert
 (or (and (= liveness_0_3 0) (= liveness_0_4 1)) (and (= liveness_0_3 1) (= liveness_0_4 2)) (and (= liveness_0_3 2) (= liveness_0_4 3)) (and (= liveness_0_3 3) (= liveness_0_4 3))))
(check-sat)
