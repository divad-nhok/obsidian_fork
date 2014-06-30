//!
//! Contains the implementation for the seismic forward model.
//!
//! \file fwdmodel/contactpoint.cpp
//! \author Nahid Akbar
//! \date 2014
//! \license Affero General Public License version 3 or later
//! \copyright (c) 2014, NICTA
//!

#include "fwd.hpp"
#include "world/voxelise.hpp"

namespace obsidian
{
  namespace fwd
  {
    //! Generate a cache object for a contact point forward model.
    //!
    //! \param boundaryInterpolation The world model interpolation parameters.
    //! \param worldSpec The world model specification.
    //! \param spec The forward model specification.
    //! \returns Forward model cache object.
    //!
    template<>
    ContactPointCache generateCache<ForwardModel::CONTACTPOINT>(const std::vector<world::InterpolatorSpec>& boundaryInterpolation,
                                                                const WorldSpec& worldSpec, const ContactPointSpec& spec)
    {
      return
      {
        boundaryInterpolation,
        world::Query(boundaryInterpolation, worldSpec, spec.locations.leftCols(2))
      };
    }

    //! Run a contact point forward model.
    //! 
    //! \param spec The forward model specification.
    //! \param cache The forward model cache generated by generateCache().
    //! \param world The world model parameters.
    //! \returns Forward model results.
    //!
    template<>
    ContactPointResults forwardModel<ForwardModel::CONTACTPOINT>(const ContactPointSpec& spec, const ContactPointCache& cache,
                                                                 const WorldParams& world)
    {
      Eigen::MatrixXd transitions = world::getTransitions(cache.boundaryInterpolation, world, cache.query); // mqueries (mlayer) x nlocations
      ContactPointResults results;
      results.readings.resize(spec.locations.rows());
      for (uint location = 0; location < spec.locations.rows(); location++)
      {
        results.readings[location].resize(spec.interfaces[location].size());
        for (uint i = 0; i < spec.interfaces[location].size(); i++)
        {
          results.readings[location](i) = transitions(spec.interfaces[location](i), location);
        }
      }
      return results;
    }

  } // namespace fwd
} // namespace obsidian