import React, { useState } from "react";
import styled from "styled-components";
import ContactImg1 from "../../assets/img/Professionals looking at a laptop.webp";
import ContactImg2 from "../../assets/img/Rocket ship.webp";
import ContactImg3 from "../../assets/img/Finger pressing Join Now.webp";
import FullButton from "../Buttons/FullButton";
import { submitContactDetails } from "../../services/contactService";

export default function Contact({ handleOpenContactForm }) {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    const contactDetails = {
      email,
      phone,
      first_name: firstName,
      last_name: lastName,
    };

    try {
      const response = await submitContactDetails(contactDetails);
      if (response.ok) {
        setSuccess(true);
        setEmail('');
        setPhone('');
        setFirstName('');
        setLastName('');
        handleOpenContactForm('Contact details submitted successfully!');
      } else {
        setError('Failed to submit contact details.');
      }
    } catch (err) {
      setError('An error occurred while submitting contact details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Wrapper id="contact">
      <div className="lightBg">
        <div className="container">
          <HeaderInfo>
            <h1 className="font40 extraBold">Signup for an early access</h1>
            <p className="font13">
              Get notified when beta testing starts. Receive updates on our latest features and services.
              <br />
            </p>
          </HeaderInfo>
          <div className="row" style={{ paddingBottom: "30px" }}>
            <div className="col-xs-12 col-sm-12 col-md-6 col-lg-6">
              <Form onSubmit={handleSubmit} autoComplete="on">
                {success && <p>Contact details submitted successfully!</p>}
                {error && <p className='redColor'>{error}</p>}
                <label className="font13">First Name:</label>
                <input
                  type="text"
                  id="fname"
                  name="fname"
                  className="font20 extraBold"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                  autoComplete="given-name"
                />
                <label className="font13">Last Name:</label>
                <input
                  type="text"
                  id="lname"
                  name="lname"
                  className="font20 extraBold"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                  autoComplete="family-name"
                />
                <label className="font13">Email:</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="font20 extraBold"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
                <label className="font13">Phone Number:</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  className="font20 extraBold"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                  autoComplete="tel"
                />
                <SubmitWrapper className="flex">
                  <button type="submit" disabled={isSubmitting} className="submit-button">
                    {isSubmitting ? 'Submitting...' : 'Get Early Access'}
                  </button>
                </SubmitWrapper>
              </Form>
            </div>
            <div className="col-xs-12 col-sm-12 col-md-6 col-lg-6 flex">
              <div style={{ width: "50%" }} className="flexNullCenter flexColumn">
                <ContactImgBox>
                  <Image src={ContactImg1} alt="office" className="radius6" width="180" height="204" />
                </ContactImgBox>
                <ContactImgBox>
                  <Image src={ContactImg2} alt="office" className="radius6" width="180" height="295" />
                </ContactImgBox>
              </div>
              <div style={{ width: "50%" }}>
                <div style={{ marginTop: "100px" }}>
                  <Image src={ContactImg3} alt="office" className="radius6" width="278" height="330" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Wrapper>
  );
}

const Wrapper = styled.section`
  width: 100%;
`;

const HeaderInfo = styled.div`
  padding: 70px 0 30px 0;
  @media (max-width: 860px) {
    text-align: center;
  }
`;

const Form = styled.form`
  padding: 70px 0 30px 0;

  input,
  textarea {
    width: 100%;
    background-color: transparent;
    border: 0px;
    outline: none;
    box-shadow: none;
    border-bottom: 1px solid #707070;
    height: 30px;
    margin-bottom: 30px;

    &:-webkit-autofill {
      box-shadow: 0 0 0px 1000px transparent inset !important;
      -webkit-text-fill-color: #000 !important;
      transition: background-color 5000s ease-in-out 0s;
    }
  }

  textarea {
    min-height: 100px;
  }

  @media (max-width: 860px) {
    padding: 30px 0;
  }
`;

const ContactImgBox = styled.div`
  max-width: 180px; 
  align-self: flex-end; 
  margin: 10px 30px 10px 0;
`;

const Image = styled.img`
  width: ${props => props.width}px;
  height: ${props => props.height}px;
  object-fit: cover;
  object-position: center;
  border-radius: 6px;
`;

const SubmitWrapper = styled.div`
  @media (max-width: 220px) {
    max-width: 220px;
    margin-bottom: 50px;
  }
`;
