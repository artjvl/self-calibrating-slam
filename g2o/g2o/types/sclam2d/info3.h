//
// Created by art on 15-06-21.
//

#ifndef G2O_INFO3_H
#define G2O_INFO3_H

#include "node_v3.h"

namespace g2o {
    class Info3 : public NodeV3 {
    public:
        Vector3 getCovDiagonal() const {
            Vector3 cov = Vector3();
            for (int i = 0; i < cov.size(); i++) {
                cov[i] = pow(_estimate[i], 2);
            }
            return cov;
        }

        Vector3 getInfoDiagonal() const {
            const Vector3& info = getCovDiagonal();
            Vector3 cov = Vector3();
            for (int i = 0; i < cov.size(); i++) {
                cov[i] = 1 / info[i];
            }
            return cov;
        }
    };
}


#endif //G2O_INFO3_H
