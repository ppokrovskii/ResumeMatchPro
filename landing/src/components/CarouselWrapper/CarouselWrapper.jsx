import Carousel from '../Carousel/Carousel';
import styles from './CarouselWrapper.module.css';
import ProjectImg1 from '../../assets/img/projects/rmp_design1-min.webp';
import ProjectImg2 from '../../assets/img/projects/rmp_design2-min.webp';
import ProjectImg3 from '../../assets/img/projects/rmp_design3-min.webp';

const CarouselWrapper = () => {
  const items = [
    {
      image: ProjectImg1,
      text: 'Upload Your Files',
      loading: 'lazy'
    },
    {
      image: ProjectImg2,
      text: 'Match CVs to Job Descriptions',
      loading: 'lazy'
    },
    {
      image: ProjectImg3,
      text: 'Match Job Descriptions to CVs',
      loading: 'lazy'
    }
  ];

  return (
    <div className={styles.carouselWrapper}>
      <Carousel items={items} />
    </div>
  );
}

export default CarouselWrapper; 