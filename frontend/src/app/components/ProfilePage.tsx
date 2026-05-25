import { useEffect, useState } from 'react';
import { CheckCircle, BadgeCheck, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useLanguage } from '../contexts/LanguageContext';
import { api } from '../services/api';
import { useNavigate } from 'react-router';

interface Job {
  id: number;
  titleKey: string;
  companyKey: string;
  locationKey: string;
}

const mockJobs: Job[] = [
  { id: 1, titleKey: 'PM Vishwakarma Scheme', companyKey: 'Govt. of India', locationKey: 'Direct Bank Transfer' },
  { id: 2, titleKey: 'PMKVY RPL Certification', companyKey: 'NSDC', locationKey: 'Official Registry' },
  { id: 3, titleKey: 'senior_stitcher', companyKey: 'local_boutique', locationKey: 'downtown' },
];

const serif = { fontFamily: '"Instrument Serif", serif' };
const sans = { fontFamily: '"Inter", system-ui, sans-serif' };

export function ProfilePage() {
  const [isJobsExpanded, setIsJobsExpanded] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const { t } = useLanguage();
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [profileData, subsData] = await Promise.all([
        api.getProfile(),
        api.getSubmissions(),
      ]);
      setProfile(profileData);
      setSubmissions(subsData);
    } catch (err) {
      console.error('Failed to fetch profile data', err);
    }
  };

  const approvedSubmission = submissions.find(s => s.status === 'approved');

  return (
    <div
      className="min-h-screen"
      style={{
        ...sans,
        background:
          'radial-gradient(1200px 600px at 50% -10%, #ffffff 0%, #F4F1EC 60%, #EDE8E0 100%)',
      }}
    >
      <div className="px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto"
        >
          {/* Hero */}
          <div className="text-center mb-10">
            <div
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-white/70 border border-zinc-200 text-emerald-600 mb-6 backdrop-blur"
              style={{ fontSize: '13px' }}
            >
              <CheckCircle size={13} /> {t('verified_artisan')}
            </div>
            <h1
              className="text-zinc-900 leading-[0.95] tracking-tight"
              style={{ ...serif, fontSize: 'clamp(40px, 6vw, 64px)' }}
            >
              {profile?.name || t('my_profile')}
            </h1>
            <p className="text-zinc-500 mt-3" style={{ fontSize: '15px' }}>
              {profile?.phone}
            </p>
          </div>

          {/* Certificate Card */}
          {approvedSubmission ? (
            <motion.div
              onClick={() => setIsJobsExpanded(!isJobsExpanded)}
              whileHover={{ y: -2 }}
              transition={{ type: 'spring', stiffness: 300 }}
              className="bg-white/90 backdrop-blur rounded-[32px] border border-zinc-200/70 p-8 cursor-pointer shadow-[0_1px_2px_rgba(16,24,40,0.04)] hover:shadow-[0_8px_32px_rgba(16,24,40,0.08)] transition-shadow mb-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 rounded-2xl bg-amber-50 border border-amber-100">
                      <BadgeCheck size={26} className="text-amber-500" strokeWidth={1.75} />
                    </div>
                    <div>
                      <h2 className="text-zinc-900" style={{ ...serif, fontSize: '32px', lineHeight: '1' }}>
                        {t(approvedSubmission.trade)} {t('expert')}
                      </h2>
                      <p className="text-zinc-500 mt-1" style={{ fontSize: '13px' }}>
                        {t('certified_credential')}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-zinc-500 mb-1" style={{ fontSize: '12px' }}>
                        {t('skill_score')}
                      </p>
                      <p className="text-zinc-900" style={{ ...serif, fontSize: '28px' }}>
                        {approvedSubmission.aiScore}<span className="text-zinc-400">/100</span>
                      </p>
                    </div>
                    <div>
                      <p className="text-zinc-500 mb-1" style={{ fontSize: '12px' }}>
                        {t('issued')}
                      </p>
                      <p className="text-zinc-900" style={{ ...serif, fontSize: '28px' }}>
                        {new Date(approvedSubmission.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="ml-6">
                  <div className="w-24 h-24 bg-white border border-zinc-200 rounded-2xl flex items-center justify-center shadow-sm">
                    <div className="text-zinc-500 text-center" style={{ fontSize: '11px' }}>
                      {t('qr_code')}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-center mt-6 text-zinc-500 gap-2">
                {isJobsExpanded ? (
                  <>
                    <ChevronUp size={16} />
                    <span style={{ fontSize: '13px' }}>{t('hide_jobs')}</span>
                  </>
                ) : (
                  <>
                    <ChevronDown size={16} />
                    <span style={{ fontSize: '13px' }}>{t('view_unlocked_jobs')}</span>
                  </>
                )}
              </div>
            </motion.div>
          ) : submissions.length > 0 ? (
            <div className="bg-white/80 backdrop-blur rounded-[32px] border border-zinc-200/70 p-12 text-center mb-4">
              <Clock size={48} className="mx-auto text-amber-500 mb-4" />
              <h2 className="text-zinc-900 mb-2" style={{ ...serif, fontSize: '32px' }}>
                Certification Pending
              </h2>
              <p className="text-zinc-500">
                A validator is currently reviewing your {submissions[0].trade} proof.
              </p>
            </div>
          ) : (
            <div className="bg-white/80 backdrop-blur rounded-[32px] border border-zinc-200/70 p-12 text-center mb-4">
              <h2 className="text-zinc-900 mb-2" style={{ ...serif, fontSize: '32px' }}>
                No Certifications Yet
              </h2>
              <p className="text-zinc-500 mb-6">
                Upload a video of your skill to get your first verified credential.
              </p>
              <button 
                onClick={() => navigate('/hub')}
                className="px-8 py-3 bg-[#2F6BFF] text-white rounded-full"
              >
                Go to Hub
              </button>
            </div>
          )}

          {/* Unlocked Jobs */}
          <AnimatePresence>
            {isJobsExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="bg-white/85 backdrop-blur border border-zinc-200/70 rounded-[28px] p-6">
                  <h3 className="text-zinc-900 mb-5" style={{ ...serif, fontSize: '26px' }}>
                    {t('unlocked_local_jobs')}
                  </h3>

                  <div className="space-y-2">
                    {mockJobs.map((job) => (
                      <motion.div
                        key={job.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: job.id * 0.08 }}
                        className="bg-zinc-50/70 border border-zinc-200/60 rounded-2xl p-4 flex items-center justify-between hover:bg-white hover:border-zinc-300 transition-colors"
                      >
                        <div>
                          <div className="text-zinc-900" style={{ fontSize: '15px' }}>
                            {t(job.titleKey)}
                          </div>
                          <div className="text-zinc-500 mt-0.5" style={{ fontSize: '13px' }}>
                            {t(job.companyKey)} · {t(job.locationKey)}
                          </div>
                        </div>
                        <button
                          className="px-5 py-2 rounded-full bg-[#2F6BFF] text-white hover:bg-[#1F58E8] transition-colors shadow-[0_1px_2px_rgba(47,107,255,0.3)]"
                          style={{ fontSize: '13px' }}
                        >
                          {t('apply')}
                        </button>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3 mt-4">
            {[
              { value: approvedSubmission ? 1 : 0, labelKey: 'certificates', accent: 'text-zinc-900' },
              { value: approvedSubmission ? 3 : 0, labelKey: 'jobs_unlocked', accent: 'text-zinc-900' },
              { value: approvedSubmission ? approvedSubmission.aiScore : 0, labelKey: 'skill_score', accent: 'text-emerald-600' },
            ].map((s) => (
              <div
                key={s.labelKey}
                className="bg-white/80 backdrop-blur border border-zinc-200/70 rounded-[24px] p-5 text-center shadow-[0_1px_2px_rgba(16,24,40,0.04)]"
              >
                <div className={`leading-none ${s.accent}`} style={{ ...serif, fontSize: '44px' }}>
                  {s.value}
                </div>
                <div className="text-zinc-500 mt-2" style={{ fontSize: '12px' }}>
                  {t(s.labelKey)}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
