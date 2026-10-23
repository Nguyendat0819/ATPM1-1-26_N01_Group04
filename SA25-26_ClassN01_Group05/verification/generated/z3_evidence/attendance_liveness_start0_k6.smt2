; benchmark generated from python API
(set-info :status unknown)
(declare-fun liveness_0_0 () Int)
(declare-fun liveness_0_1 () Int)
(declare-fun liveness_0_2 () Int)
(declare-fun liveness_0_3 () Int)
(declare-fun liveness_0_4 () Int)
(declare-fun liveness_0_5 () Int)
(declare-fun liveness_0_6 () Int)
(assert
 (let (($x206 (= liveness_0_0 5)))
 (let (($x120 (= liveness_0_0 4)))
 (let (($x163 (= liveness_0_0 3)))
 (let (($x76 (= liveness_0_0 2)))
 (let (($x141 (= liveness_0_0 1)))
 (let (($x143 (= liveness_0_0 0)))
 (or $x143 $x141 $x76 $x163 $x120 $x206))))))))
(assert
 (not (or (= liveness_0_0 3))))
(assert
 (let (($x302 (= liveness_0_1 5)))
 (let (($x18 (= liveness_0_1 4)))
 (let (($x22 (= liveness_0_1 3)))
 (let (($x283 (= liveness_0_1 2)))
 (let (($x292 (= liveness_0_1 1)))
 (let (($x264 (= liveness_0_1 0)))
 (or $x264 $x292 $x283 $x22 $x18 $x302))))))))
(assert
 (not (or (= liveness_0_1 3))))
(assert
 (let (($x38 (= liveness_0_2 5)))
 (let (($x19 (= liveness_0_2 4)))
 (let (($x153 (= liveness_0_2 3)))
 (let (($x198 (= liveness_0_2 2)))
 (let (($x47 (= liveness_0_2 1)))
 (let (($x42 (= liveness_0_2 0)))
 (or $x42 $x47 $x198 $x153 $x19 $x38))))))))
(assert
 (not (or (= liveness_0_2 3))))
(assert
 (let (($x70 (= liveness_0_3 5)))
 (let (($x39 (= liveness_0_3 4)))
 (let (($x106 (= liveness_0_3 3)))
 (let (($x26 (= liveness_0_3 2)))
 (let (($x137 (= liveness_0_3 1)))
 (let (($x209 (= liveness_0_3 0)))
 (or $x209 $x137 $x26 $x106 $x39 $x70))))))))
(assert
 (not (or (= liveness_0_3 3))))
(assert
 (let (($x124 (= liveness_0_4 5)))
 (let (($x156 (= liveness_0_4 4)))
 (let (($x117 (= liveness_0_4 3)))
 (let (($x122 (= liveness_0_4 2)))
 (let (($x184 (= liveness_0_4 1)))
 (let (($x158 (= liveness_0_4 0)))
 (or $x158 $x184 $x122 $x117 $x156 $x124))))))))
(assert
 (not (or (= liveness_0_4 3))))
(assert
 (let (($x296 (= liveness_0_5 5)))
 (let (($x299 (= liveness_0_5 4)))
 (let (($x256 (= liveness_0_5 3)))
 (let (($x280 (= liveness_0_5 2)))
 (let (($x10 (= liveness_0_5 1)))
 (let (($x228 (= liveness_0_5 0)))
 (or $x228 $x10 $x280 $x256 $x299 $x296))))))))
(assert
 (not (or (= liveness_0_5 3))))
(assert
 (let (($x313 (= liveness_0_6 5)))
 (let (($x312 (= liveness_0_6 4)))
 (let (($x311 (= liveness_0_6 3)))
 (let (($x310 (= liveness_0_6 2)))
 (let (($x309 (= liveness_0_6 1)))
 (let (($x308 (= liveness_0_6 0)))
 (or $x308 $x309 $x310 $x311 $x312 $x313))))))))
(assert
 (not (or (= liveness_0_6 3))))
(assert
 (= liveness_0_0 2))
(assert
 (or (and (= liveness_0_0 0) (= liveness_0_1 1)) (and (= liveness_0_0 1) (= liveness_0_1 5)) (and (= liveness_0_0 1) (= liveness_0_1 2)) (and (= liveness_0_0 2) (= liveness_0_1 3)) (and (= liveness_0_0 5) (= liveness_0_1 0)) (and (= liveness_0_0 3) (= liveness_0_1 4)) (and (= liveness_0_0 4) (= liveness_0_1 0))))
(assert
 (or (and (= liveness_0_1 0) (= liveness_0_2 1)) (and (= liveness_0_1 1) (= liveness_0_2 5)) (and (= liveness_0_1 1) (= liveness_0_2 2)) (and (= liveness_0_1 2) (= liveness_0_2 3)) (and (= liveness_0_1 5) (= liveness_0_2 0)) (and (= liveness_0_1 3) (= liveness_0_2 4)) (and (= liveness_0_1 4) (= liveness_0_2 0))))
(assert
 (or (and (= liveness_0_2 0) (= liveness_0_3 1)) (and (= liveness_0_2 1) (= liveness_0_3 5)) (and (= liveness_0_2 1) (= liveness_0_3 2)) (and (= liveness_0_2 2) (= liveness_0_3 3)) (and (= liveness_0_2 5) (= liveness_0_3 0)) (and (= liveness_0_2 3) (= liveness_0_3 4)) (and (= liveness_0_2 4) (= liveness_0_3 0))))
(assert
 (or (and (= liveness_0_3 0) (= liveness_0_4 1)) (and (= liveness_0_3 1) (= liveness_0_4 5)) (and (= liveness_0_3 1) (= liveness_0_4 2)) (and (= liveness_0_3 2) (= liveness_0_4 3)) (and (= liveness_0_3 5) (= liveness_0_4 0)) (and (= liveness_0_3 3) (= liveness_0_4 4)) (and (= liveness_0_3 4) (= liveness_0_4 0))))
(assert
 (or (and (= liveness_0_4 0) (= liveness_0_5 1)) (and (= liveness_0_4 1) (= liveness_0_5 5)) (and (= liveness_0_4 1) (= liveness_0_5 2)) (and (= liveness_0_4 2) (= liveness_0_5 3)) (and (= liveness_0_4 5) (= liveness_0_5 0)) (and (= liveness_0_4 3) (= liveness_0_5 4)) (and (= liveness_0_4 4) (= liveness_0_5 0))))
(assert
 (or (and (= liveness_0_5 0) (= liveness_0_6 1)) (and (= liveness_0_5 1) (= liveness_0_6 5)) (and (= liveness_0_5 1) (= liveness_0_6 2)) (and (= liveness_0_5 2) (= liveness_0_6 3)) (and (= liveness_0_5 5) (= liveness_0_6 0)) (and (= liveness_0_5 3) (= liveness_0_6 4)) (and (= liveness_0_5 4) (= liveness_0_6 0))))
(check-sat)
