; benchmark generated from python API
(set-info :status unknown)
(declare-fun liveness_0_0 () Int)
(declare-fun liveness_0_1 () Int)
(declare-fun liveness_0_2 () Int)
(declare-fun liveness_0_3 () Int)
(declare-fun liveness_0_4 () Int)
(assert
 (let (($x80 (= liveness_0_0 3)))
 (let (($x341 (= liveness_0_0 2)))
 (let (($x18 (= liveness_0_0 1)))
 (let (($x173 (= liveness_0_0 0)))
 (or $x173 $x18 $x341 $x80))))))
(assert
 (not (or (= liveness_0_0 2) (= liveness_0_0 3))))
(assert
 (let (($x153 (= liveness_0_1 3)))
 (let (($x292 (= liveness_0_1 2)))
 (let (($x62 (= liveness_0_1 1)))
 (let (($x276 (= liveness_0_1 0)))
 (or $x276 $x62 $x292 $x153))))))
(assert
 (not (or (= liveness_0_1 2) (= liveness_0_1 3))))
(assert
 (let (($x38 (= liveness_0_2 3)))
 (let (($x299 (= liveness_0_2 2)))
 (let (($x364 (= liveness_0_2 1)))
 (let (($x106 (= liveness_0_2 0)))
 (or $x106 $x364 $x299 $x38))))))
(assert
 (not (or (= liveness_0_2 2) (= liveness_0_2 3))))
(assert
 (let (($x273 (= liveness_0_3 3)))
 (let (($x208 (= liveness_0_3 2)))
 (let (($x146 (= liveness_0_3 1)))
 (let (($x210 (= liveness_0_3 0)))
 (or $x210 $x146 $x208 $x273))))))
(assert
 (not (or (= liveness_0_3 2) (= liveness_0_3 3))))
(assert
 (let (($x294 (= liveness_0_4 3)))
 (let (($x51 (= liveness_0_4 2)))
 (let (($x284 (= liveness_0_4 1)))
 (let (($x30 (= liveness_0_4 0)))
 (or $x30 $x284 $x51 $x294))))))
(assert
 (not (or (= liveness_0_4 2) (= liveness_0_4 3))))
(assert
 (= liveness_0_0 1))
(assert
 (or (and (= liveness_0_0 0) (= liveness_0_1 1)) (and (= liveness_0_0 1) (= liveness_0_1 2)) (and (= liveness_0_0 1) (= liveness_0_1 3)) (and (= liveness_0_0 2) (= liveness_0_1 0)) (and (= liveness_0_0 3) (= liveness_0_1 0))))
(assert
 (or (and (= liveness_0_1 0) (= liveness_0_2 1)) (and (= liveness_0_1 1) (= liveness_0_2 2)) (and (= liveness_0_1 1) (= liveness_0_2 3)) (and (= liveness_0_1 2) (= liveness_0_2 0)) (and (= liveness_0_1 3) (= liveness_0_2 0))))
(assert
 (or (and (= liveness_0_2 0) (= liveness_0_3 1)) (and (= liveness_0_2 1) (= liveness_0_3 2)) (and (= liveness_0_2 1) (= liveness_0_3 3)) (and (= liveness_0_2 2) (= liveness_0_3 0)) (and (= liveness_0_2 3) (= liveness_0_3 0))))
(assert
 (or (and (= liveness_0_3 0) (= liveness_0_4 1)) (and (= liveness_0_3 1) (= liveness_0_4 2)) (and (= liveness_0_3 1) (= liveness_0_4 3)) (and (= liveness_0_3 2) (= liveness_0_4 0)) (and (= liveness_0_3 3) (= liveness_0_4 0))))
(check-sat)
