; benchmark generated from python API
(set-info :status unknown)
(declare-fun state_4_0 () Int)
(declare-fun state_4_1 () Int)
(declare-fun state_4_2 () Int)
(declare-fun state_4_3 () Int)
(declare-fun state_4_4 () Int)
(assert
 (let (($x375 (= state_4_0 3)))
 (let (($x207 (= state_4_0 2)))
 (let (($x10 (= state_4_0 1)))
 (let (($x492 (= state_4_0 0)))
 (or $x492 $x10 $x207 $x375))))))
(assert
 (let (($x500 (= state_4_1 3)))
 (let (($x218 (= state_4_1 2)))
 (let (($x154 (= state_4_1 1)))
 (let (($x287 (= state_4_1 0)))
 (or $x287 $x154 $x218 $x500))))))
(assert
 (let (($x262 (= state_4_2 3)))
 (let (($x362 (= state_4_2 2)))
 (let (($x507 (= state_4_2 1)))
 (let (($x170 (= state_4_2 0)))
 (or $x170 $x507 $x362 $x262))))))
(assert
 (let (($x168 (= state_4_3 3)))
 (let (($x377 (= state_4_3 2)))
 (let (($x92 (= state_4_3 1)))
 (let (($x401 (= state_4_3 0)))
 (or $x401 $x92 $x377 $x168))))))
(assert
 (let (($x428 (= state_4_4 3)))
 (let (($x378 (= state_4_4 2)))
 (let (($x386 (= state_4_4 1)))
 (or (= state_4_4 0) $x386 $x378 $x428)))))
(assert
 (= state_4_0 0))
(assert
 (or (and (= state_4_0 0) (= state_4_1 1)) (and (= state_4_0 1) (= state_4_1 2)) (and (= state_4_0 2) (= state_4_1 3)) (and (= state_4_0 3) (= state_4_1 3))))
(assert
 (or (and (= state_4_1 0) (= state_4_2 1)) (and (= state_4_1 1) (= state_4_2 2)) (and (= state_4_1 2) (= state_4_2 3)) (and (= state_4_1 3) (= state_4_2 3))))
(assert
 (or (and (= state_4_2 0) (= state_4_3 1)) (and (= state_4_2 1) (= state_4_3 2)) (and (= state_4_2 2) (= state_4_3 3)) (and (= state_4_2 3) (= state_4_3 3))))
(assert
 (or (and (= state_4_3 0) (= state_4_4 1)) (and (= state_4_3 1) (= state_4_4 2)) (and (= state_4_3 2) (= state_4_4 3)) (and (= state_4_3 3) (= state_4_4 3))))
(assert
 (let (($x428 (= state_4_4 3)))
(let (($x401 (= state_4_3 0)))
(let (($x25 (and $x401 $x428)))
(let (($x92 (= state_4_3 1)))
(let (($x425 (and $x92 $x428)))
(let (($x378 (= state_4_4 2)))
(let (($x168 (= state_4_3 3)))
(let (($x203 (and $x168 $x378)))
(let (($x491 (and $x401 $x378)))
(let (($x377 (= state_4_3 2)))
(let (($x285 (and $x377 $x378)))
(let (($x386 (= state_4_4 1)))
(let (($x509 (and $x168 $x386)))
(let (($x18 (and $x377 $x386)))
(let (($x513 (and $x92 $x386)))
(or $x513 $x18 $x509 $x285 $x491 $x203 $x425 $x25)))))))))))))))))
(check-sat)
