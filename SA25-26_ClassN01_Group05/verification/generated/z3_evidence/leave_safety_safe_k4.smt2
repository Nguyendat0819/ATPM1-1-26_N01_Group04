; benchmark generated from python API
(set-info :status unknown)
(declare-fun state_4_0 () Int)
(declare-fun state_4_1 () Int)
(declare-fun state_4_2 () Int)
(declare-fun state_4_3 () Int)
(declare-fun state_4_4 () Int)
(assert
 (let (($x69 (= state_4_0 3)))
 (let (($x263 (= state_4_0 2)))
 (let (($x304 (= state_4_0 1)))
 (let (($x319 (= state_4_0 0)))
 (or $x319 $x304 $x263 $x69))))))
(assert
 (let (($x283 (= state_4_1 3)))
 (let (($x301 (= state_4_1 2)))
 (let (($x324 (= state_4_1 1)))
 (let (($x305 (= state_4_1 0)))
 (or $x305 $x324 $x301 $x283))))))
(assert
 (let (($x352 (= state_4_2 3)))
 (let (($x288 (= state_4_2 2)))
 (let (($x317 (= state_4_2 1)))
 (let (($x307 (= state_4_2 0)))
 (or $x307 $x317 $x288 $x352))))))
(assert
 (let (($x350 (= state_4_3 3)))
 (let (($x32 (= state_4_3 2)))
 (let (($x306 (= state_4_3 1)))
 (let (($x128 (= state_4_3 0)))
 (or $x128 $x306 $x32 $x350))))))
(assert
 (let (($x262 (= state_4_4 3)))
 (let (($x204 (= state_4_4 2)))
 (let (($x25 (= state_4_4 1)))
 (let (($x124 (= state_4_4 0)))
 (or $x124 $x25 $x204 $x262))))))
(assert
 (= state_4_0 0))
(assert
 (or (and (= state_4_0 0) (= state_4_1 1)) (and (= state_4_0 1) (= state_4_1 2)) (and (= state_4_0 1) (= state_4_1 3)) (and (= state_4_0 2) (= state_4_1 0)) (and (= state_4_0 3) (= state_4_1 0))))
(assert
 (or (and (= state_4_1 0) (= state_4_2 1)) (and (= state_4_1 1) (= state_4_2 2)) (and (= state_4_1 1) (= state_4_2 3)) (and (= state_4_1 2) (= state_4_2 0)) (and (= state_4_1 3) (= state_4_2 0))))
(assert
 (or (and (= state_4_2 0) (= state_4_3 1)) (and (= state_4_2 1) (= state_4_3 2)) (and (= state_4_2 1) (= state_4_3 3)) (and (= state_4_2 2) (= state_4_3 0)) (and (= state_4_2 3) (= state_4_3 0))))
(assert
 (or (and (= state_4_3 0) (= state_4_4 1)) (and (= state_4_3 1) (= state_4_4 2)) (and (= state_4_3 1) (= state_4_4 3)) (and (= state_4_3 2) (= state_4_4 0)) (and (= state_4_3 3) (= state_4_4 0))))
(assert
 (let (($x262 (= state_4_4 3)))
(let (($x350 (= state_4_3 3)))
(let (($x200 (and $x350 $x262)))
(let (($x128 (= state_4_3 0)))
(let (($x86 (and $x128 $x262)))
(let (($x32 (= state_4_3 2)))
(let (($x179 (and $x32 $x262)))
(let (($x204 (= state_4_4 2)))
(let (($x303 (and $x350 $x204)))
(let (($x230 (and $x128 $x204)))
(let (($x48 (and $x32 $x204)))
(or $x48 $x230 $x303 $x179 $x86 $x200)))))))))))))
(check-sat)
