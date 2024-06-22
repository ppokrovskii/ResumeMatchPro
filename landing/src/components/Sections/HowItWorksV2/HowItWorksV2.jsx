// import React, { useState } from 'react';
// import styles from './HowItWorksV2.module.css';
import Carousel from '../../Carousel/Carousel';
import ProjectImg1 from '../../../assets/img/projects/rmp_design1.png';
import ProjectImg2 from '../../../assets/img/projects/rmp_design2.png';
import ProjectImg3 from '../../../assets/img/projects/rmp_design3.png';

const HowItWorksV2 = () => {
  // const [activeImage, setActiveImage] = useState(null);

  const items = [
    {
      image: ProjectImg1,
      text: 'Upload Your Files'
    },
    {
      image: ProjectImg2,
      text: 'Match CVs to Job Descriptions'
    },
    {
      image: ProjectImg3,
      text: 'Match Job Descriptions to CVs'
    }
  ];

  return (
    <div id="projects">
      <Carousel items={items} />
    </div>
  );
}

export default HowItWorksV2;